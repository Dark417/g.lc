package com.lc.x;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration;

/**
 * Entry point for every 1x slice.
 * - Starts with no cloud access: every slice is off until x.<slice>.enabled=true.
 * - DataSource auto-config is off: the Aurora slice builds its own Hikari pools (writer + reader).
 * - Kafka auto-config is off: the Kafka slice builds its own MSK-aware factories.
 */
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class, KafkaAutoConfiguration.class})
public class XApplication {

    public static void main(String[] args) {
        SpringApplication.run(XApplication.class, args);
    }
}
