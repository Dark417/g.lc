package com.lc.x.x03_01_aurora.domain;

import java.util.List;

/**
 * One page of results.
 * - next: opaque token for the next page (keyset cursor or next page number); null when there is no next page.
 */
public record Page<T>(List<T> items, String next) {

    public Page {
        items = List.copyOf(items);
    }

    public boolean hasNext() {
        return next != null;
    }
}
