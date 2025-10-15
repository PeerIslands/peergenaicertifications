// Test script to verify Supabase migration
// Run with: tsx test-supabase-migration.js

import dotenv from 'dotenv';
import { getSupabaseStorage } from './server/supabase-storage.ts';

// Load environment variables
dotenv.config();

async function testSupabaseConnection() {
  try {
    console.log('Testing Supabase connection...');
    
    const storage = await getSupabaseStorage();
    console.log('✅ Supabase connection successful');
    
    // Test getting stats
    const stats = await storage.getStats();
    console.log('✅ Database stats:', stats);
    
    // Test creating a test document
    const testDocument = await storage.createDocument({
      name: 'Test Document',
      size: 1024,
      status: 'ready'
    });
    console.log('✅ Test document created:', testDocument.id);
    
    // Test creating a test chunk
    const testChunk = await storage.createDocumentChunk({
      document_id: testDocument.id,
      content: 'This is a test chunk for migration verification.',
      chunk_index: 0,
      metadata: { test: true }
    });
    console.log('✅ Test chunk created:', testChunk.id);
    
    // Test search functionality
    const searchResults = await storage.searchSimilarChunks([0.1, 0.2, 0.3], 5);
    console.log('✅ Search functionality working, found', searchResults.length, 'results');
    
    // Clean up test data
    await storage.deleteDocument(testDocument.id);
    console.log('✅ Test data cleaned up');
    
    console.log('\n🎉 All tests passed! Supabase migration is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Full error:', error);
    process.exit(1);
  }
}

// Run the test
testSupabaseConnection();
