package com.lc.a;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the 1A Java slices.
 * - Starts with no cloud access: every slice is off until a.<slice>.enabled=true.
 */
@SpringBootApplication
public class AApplication {

    public static void main(String[] args) {
        SpringApplication.run(AApplication.class, args);
    }
}
