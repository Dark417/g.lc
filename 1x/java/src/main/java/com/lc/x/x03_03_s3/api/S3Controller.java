package com.lc.x.x03_03_s3.api;

import com.lc.x.x03_03_s3.domain.CreateResult;
import com.lc.x.x03_03_s3.domain.LakeStore;
import com.lc.x.x03_03_s3.domain.ListingPage;
import com.lc.x.x03_03_s3.domain.ObjectInfo;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Duration;
import java.util.Map;

/** Thin REST adapter under /s3: maps HTTP to LakeStore and 412 to HTTP 409/200 semantics. */
@RestController
@RequestMapping("/s3")
@ConditionalOnProperty(name = "x.s3.enabled", havingValue = "true")
public class S3Controller {

    private final LakeStore store;

    public S3Controller(LakeStore store) {
        this.store = store;
    }

    @GetMapping("/head")
    public ObjectInfo head(@RequestParam String key) {
        return store.head(key);
    }

    @GetMapping("/list")
    public ListingPage list(@RequestParam(defaultValue = "") String prefix) {
        return store.listFolder(prefix);
    }

    @GetMapping("/presign-get")
    public Map<String, String> presignGet(@RequestParam String key, @RequestParam(defaultValue = "300") long seconds) {
        return Map.of("url", store.presignGet(key, Duration.ofSeconds(seconds)));
    }

    // Create-only: 201 when created, 409 when the key already exists.
    @PutMapping("/create-only")
    public ResponseEntity<CreateResult> createOnly(@RequestParam String key, @RequestBody byte[] body) {
        CreateResult r = store.putIfAbsent(key, body);
        return ResponseEntity.status(r.created() ? HttpStatus.CREATED : HttpStatus.CONFLICT).body(r);
    }
}
