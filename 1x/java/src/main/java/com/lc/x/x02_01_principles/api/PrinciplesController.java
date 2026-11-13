package com.lc.x.x02_01_principles.api;

import com.lc.x.x02_01_principles.PrinciplesCatalog;
import com.lc.x.x02_01_principles.spring.SpringPrinciplesDemo;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.function.Supplier;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * Thin inbound adapter: GET /principles lists names, GET /principles/{name} runs that demo.
 * - Parts A/B come from PrinciplesCatalog; Part C from the container-built SpringPrinciplesDemo.
 * - Catch: demos mutate in-memory state (counters, repos), so repeated calls show growing counts.
 */
@RestController
@RequestMapping("/principles")
@ConditionalOnProperty(name = "x.principles.enabled", havingValue = "true")
public class PrinciplesController {

    private final Map<String, Supplier<String>> demos = new LinkedHashMap<>();

    public PrinciplesController(SpringPrinciplesDemo spring) {
        demos.putAll(PrinciplesCatalog.plain());
        demos.putAll(spring.demos());
    }

    // Lists every demo name in doc order.
    // Use to discover valid {name} values.
    // Catch: none; read-only.
    @GetMapping
    public Set<String> list() {
        return demos.keySet();
    }

    // Runs one principle's demo and returns its trace.
    // Use: curl localhost:8080/principles/aop
    // Catch: unknown names are a 404, not a 500 (fail fast with a clear message).
    @GetMapping("/{name}")
    public Map<String, String> show(@PathVariable String name) {
        Supplier<String> demo = demos.get(name);
        if (demo == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "unknown principle '" + name + "'; try " + demos.keySet());
        }
        return Map.of("principle", name, "output", demo.get());
    }
}
