package com.lc.x.domain._03db_03s3;

import java.util.List;

/** One logical listing: objects directly under the prefix + "folders" (common prefixes). */
public record ListingPage(List<String> keys, List<String> commonPrefixes, int pagesFetched) {
}
