import 'dotenv/config';
import pg from 'pg';
const { Client } = pg;

async function testConnection() {
  const jdbcUrl = process.env.JDBC_URL || 'jdbc:postgresql://35.193.24.101:5432/myappdb?user=myappuser&password=ChangeThisPassword123!';
  const match = jdbcUrl.match(/jdbc:postgresql:\/\/([^:]+):(\d+)\/([^?]+)\?user=([^&]+)&password=(.+)/);
  
  if (!match) {
    console.error('Invalid JDBC URL format');
    process.exit(1);
  }
  
  const [, host, port, database, user, password] = match;
  const connectionString = `postgresql://${user}:${encodeURIComponent(password)}@${host}:${port}/${database}`;
  
  console.log(`Testing connection to: ${host}:${port}/${database}`);
  
  const client = new Client({
    connectionString,
    ssl: false,
  });
  
  try {
    await client.connect();
    console.log('✅ Connected successfully!');
    
    // Check if tables exist
    const tablesResult = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
        AND table_name IN ('documents', 'document_chunks', 'search_queries')
      ORDER BY table_name
    `);
    
    console.log('\n📊 Tables found:');
    if (tablesResult.rows.length === 0) {
      console.log('❌ No tables found! Please run the migration SQL in DBeaver.');
    } else {
      tablesResult.rows.forEach(row => {
        console.log(`  ✓ ${row.table_name}`);
      });
    }
    
    await client.end();
  } catch (error) {
    console.error('❌ Connection failed:', (error as Error).message);
    process.exit(1);
  }
}

testConnection();

