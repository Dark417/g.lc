package com.lc.x.domain._03db_02dynamodb;

import java.util.List;

/**
 * One page of results + an opaque cursor.
 * - nextCursor == null is the ONLY end-of-results signal; a short or empty page is not.
 */
public record CursorPage<T>(List<T> items, String nextCursor) {
}
