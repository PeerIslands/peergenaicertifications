import 'dotenv/config';
import { ragService } from './rag';
import { mongodbService } from './mongodb';

async function testRAG() {
  try {
    console.log('Testing RAG functionality...');
    
    // Connect to MongoDB
    await mongodbService.connect();
    console.log('✓ Connected to MongoDB');
    
    // Check RAG service status
    const stats = await ragService.getKnowledgeBaseStats();
    console.log(`✓ RAG Service Status:`, stats);
    
    if (stats.documentCount > 0) {
      console.log('✓ Knowledge base has documents');
      
      // Test search functionality
      const testQuery = 'artificial intelligence';
      console.log(`\nTesting search with query: "${testQuery}"`);
      
      const results = await ragService.retrieveRelevantDocuments(testQuery, 3);
      console.log(`✓ Found ${results.length} relevant documents:`);
      
      results.forEach((doc, index) => {
        console.log(`  ${index + 1}. Similarity: ${(doc as any).similarity?.toFixed(3)}`);
        console.log(`     Content: ${doc.content.substring(0, 100)}...`);
        console.log(`     Metadata:`, doc.metadata);
        console.log('');
      });
    } else {
      console.log('⚠ Knowledge base is empty - no documents found');
    }
    
    console.log('✓ RAG test completed successfully!');
  } catch (error) {
    console.error('✗ RAG test failed:', error);
  } finally {
    await mongodbService.disconnect();
    process.exit(0);
  }
}

// Run the test
testRAG();
