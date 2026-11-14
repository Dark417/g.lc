import { Pipe, PipeTransform } from '@angular/core';

/**
 * Tiny, safe Markdown subset for model replies: escape first, then **bold**, *italic*,
 * `code`, "- " / "1. " lists, and line breaks. Angular sanitizes [innerHTML] as well.
 */
@Pipe({ name: 'md' })
export class MarkdownPipe implements PipeTransform {
  transform(text: string | null | undefined): string {
    if (!text) return '';
    const esc = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const inline = (s: string) =>
      s
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/(^|[^*])\*(?!\s)(.+?)\*/g, '$1<em>$2</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');
    const out: string[] = [];
    let list: 'ul' | 'ol' | null = null;
    for (const line of esc.split('\n')) {
      const ul = line.match(/^\s*[-*]\s+(.*)$/);
      const ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
      const kind = ul ? 'ul' : ol ? 'ol' : null;
      if (list && kind !== list) {
        out.push(`</${list}>`);
        list = null;
      }
      if (kind) {
        if (!list) out.push(`<${(list = kind)}>`);
        out.push(`<li>${inline((ul ?? ol)![1])}</li>`);
      } else {
        out.push(line.trim() ? `<p>${inline(line)}</p>` : '');
      }
    }
    if (list) out.push(`</${list}>`);
    return out.join('');
  }
}
