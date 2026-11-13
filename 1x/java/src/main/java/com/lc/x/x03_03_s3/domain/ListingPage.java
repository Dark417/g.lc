package com.lc.x.x03_03_s3.domain;

import java.util.List;

/** One logical listing: objects directly under the prefix + "folders" (common prefixes). */
public record ListingPage(List<String> keys, List<String> commonPrefixes, int pagesFetched) {
}
