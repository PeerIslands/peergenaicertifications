import 'dotenv/config';
import pg from 'pg';
import { CREATE_TABLES_SQL } from './shared/supabase-schema';

const { Client } = pg;

// Function to parse JDBC connection string
function parseJdbcUrl(jdbcUrl: string): { host: string; port: number; database: string; user: string; password: string } {
  const match = jdbcUrl.match(/jdbc:postgresql:\/\/([^:]+):(\d+)\/([^?]+)\?user=([^&]+)&password=(.+)/);
  if (!match) {
    throw new Error('Invalid JDBC connection string format. Expected: jdbc:postgresql://host:port/db?user=user&password=pass');
  }
  
  const [, host, port, database, user, password] = match;
  return {
    host,
    port: parseInt(port, 10),
    database,
    user,
    password
  };
}

// Function to split SQL into statements, handling dollar-quoted strings
function splitSQLStatements(sql: string): string[] {
  const statements: string[] = [];
  let currentStatement = '';
  let inDollarQuote = false;
  let dollarTag = '';
  let i = 0;

  while (i < sql.length) {
    const char = sql[i];

    // Check for dollar-quoted strings ($$ or $tag$ ... $tag$)
    if (char === '$' && !inDollarQuote) {
      // Find the dollar tag
      let tagEnd = i + 1;
      while (tagEnd < sql.length && sql[tagEnd] !== '$') {
        tagEnd++;
      }
      if (tagEnd < sql.length) {
        dollarTag = sql.substring(i, tagEnd + 1);
        inDollarQuote = true;
        currentStatement += dollarTag;
        i = tagEnd + 1;
        continue;
      }
    } else if (inDollarQuote) {
      // Check if we're at the end of the dollar-quoted string
      if (i + dollarTag.length <= sql.length && 
          sql.substring(i, i + dollarTag.length) === dollarTag) {
        currentStatement += dollarTag;
        i += dollarTag.length;
        inDollarQuote = false;
        dollarTag = '';
        continue;
      }
    }

    // Check for statement terminator (semicolon outside dollar quotes)
    if (char === ';' && !inDollarQuote) {
      currentStatement += char;
      const trimmed = currentStatement.trim();
      if (trimmed && !trimmed.startsWith('--') && trimmed.length > 0) {
        statements.push(trimmed);
      }
      currentStatement = '';
      i++;
      continue;
    }

    currentStatement += char;
    i++;
  }

  // Add remaining statement if any
  const trimmed = currentStatement.trim();
  if (trimmed && !trimmed.startsWith('--') && trimmed.length > 0) {
    statements.push(trimmed);
  }

  return statements;
}

async function migrate() {
  const jdbcUrl = process.env.JDBC_URL || 'jdbc:postgresql://35.193.24.101:5432/myappdb?user=myappuser&password=ChangeThisPassword123!';
  const config = parseJdbcUrl(jdbcUrl);

  console.log(`Connecting to PostgreSQL at ${config.host}:${config.port}/${config.database}...`);

  const client = new Client({
    host: config.host,
    port: config.port,
    database: config.database,
    user: config.user,
    password: config.password,
    ssl: false, // Set to true if your database requires SSL
  });

  try {
    await client.connect();
    console.log('Connected successfully!');

    // Remove RLS policies from the SQL (we don't need them for regular PostgreSQL)
    let migrationSQL = CREATE_TABLES_SQL
      .replace(/-- Enable RLS on all tables[\s\S]*?CREATE POLICY[\s\S]*?;[\s\S]*?CREATE POLICY[\s\S]*?;[\s\S]*?CREATE POLICY[\s\S]*?;/g, '')
      .replace(/ALTER TABLE.*ENABLE ROW LEVEL SECURITY;[\s\S]*?/g, '');

    console.log('Creating tables and indexes...');
    console.log(`SQL length: ${migrationSQL.length} characters`);
    console.log(`Contains CREATE TABLE: ${migrationSQL.includes('CREATE TABLE')}`);
    console.log(`Contains CREATE EXTENSION: ${migrationSQL.includes('CREATE EXTENSION')}\n`);
    
    // Split SQL into proper statements
    const statements = splitSQLStatements(migrationSQL);
    
    console.log(`Found ${statements.length} SQL statements to execute`);
    if (statements.length > 0) {
      console.log('All statements:');
      statements.forEach((stmt, idx) => {
        const preview = stmt.substring(0, 100).replace(/\s+/g, ' ');
        console.log(`  ${idx + 1}. ${preview}...`);
      });
      console.log('');
    }

    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      if (statement.trim()) {
        try {
          await client.query(statement);
          const preview = statement.substring(0, 70).replace(/\s+/g, ' ');
          console.log(`✓ [${i + 1}/${statements.length}] Executed: ${preview}...`);
        } catch (err: any) {
          // Ignore "already exists" errors
          if (err.message.includes('already exists') || 
              err.code === '42P07' || 
              err.code === '42710' || 
              err.code === '42723' ||
              err.code === '42704') {
            const preview = statement.substring(0, 70).replace(/\s+/g, ' ');
            console.log(`⚠ [${i + 1}/${statements.length}] Skipped (already exists): ${preview}...`);
          } else {
            const preview = statement.substring(0, 70).replace(/\s+/g, ' ');
            console.error(`✗ [${i + 1}/${statements.length}] Error: ${preview}...`);
            console.error(`  ${err.message} (code: ${err.code})`);
            // Continue with other statements - some might succeed
          }
        }
      }
    }

    // Create the vector search function if pgvector is available
    console.log('\nCreating vector search function...');
    try {
      await client.query(`
        CREATE OR REPLACE FUNCTION match_document_chunks(
          query_embedding VECTOR(384),
          match_threshold FLOAT DEFAULT 0.7,
          match_count INT DEFAULT 10
        )
        RETURNS TABLE (
          id UUID,
          document_id UUID,
          content TEXT,
          page_number INTEGER,
          chunk_index INTEGER,
          metadata JSONB,
          similarity FLOAT
        ) AS $$
        BEGIN
          RETURN QUERY
          SELECT
            document_chunks.id,
            document_chunks.document_id,
            document_chunks.content,
            document_chunks.page_number,
            document_chunks.chunk_index,
            document_chunks.metadata,
            1 - (document_chunks.embedding <=> query_embedding) AS similarity
          FROM document_chunks
          WHERE document_chunks.embedding IS NOT NULL
            AND 1 - (document_chunks.embedding <=> query_embedding) > match_threshold
          ORDER BY document_chunks.embedding <=> query_embedding
          LIMIT match_count;
        END;
        $$ LANGUAGE plpgsql;
      `);
      console.log('✓ Vector search function created');
    } catch (error: any) {
      if (error.message.includes('already exists') || error.code === '42710') {
        console.log('⚠ Vector search function already exists');
      } else {
        console.warn('⚠ Could not create vector search function (pgvector may not be installed):', error.message);
      }
    }

    console.log('\n✅ Migration completed successfully!');
    console.log('\nNote: If you need pgvector extension for vector search, run:');
    console.log('  CREATE EXTENSION IF NOT EXISTS vector;');
    console.log('\nYou can do this manually in your database or it will be created automatically when needed.');

  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  } finally {
    await client.end();
  }
}

migrate();
