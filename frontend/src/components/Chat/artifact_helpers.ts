export function strip_artifact_tags(text: string): string {
  const pattern = /<artifact\s+type="[^"]+"\s+title="[^"]+">[\s\S]*?<\/artifact>/gi;
  return text.replace(pattern, '').trim();
}
