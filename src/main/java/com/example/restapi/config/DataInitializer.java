package com.example.restapi.config;

import com.example.restapi.model.User;
import com.example.restapi.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {
    
    private final UserRepository userRepository;
    
    @Autowired
    public DataInitializer(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    @Override
    public void run(String... args) throws Exception {
        // Clear existing data
        userRepository.deleteAll();
        
        // Create sample users
        User user1 = new User("John Doe", "john.doe@example.com", "Software Developer");
        User user2 = new User("Jane Smith", "jane.smith@example.com", "Product Manager");
        User user3 = new User("Bob Johnson", "bob.johnson@example.com", "Data Analyst");
        User user4 = new User("Alice Brown", "alice.brown@example.com", "UX Designer");
        User user5 = new User("Charlie Wilson", "charlie.wilson@example.com", "DevOps Engineer");
        
        // Save users to database
        userRepository.save(user1);
        userRepository.save(user2);
        userRepository.save(user3);
        userRepository.save(user4);
        userRepository.save(user5);
        
        System.out.println("Sample data initialized successfully!");
        System.out.println("Total users created: " + userRepository.count());
    }
}
