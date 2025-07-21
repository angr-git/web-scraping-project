def parse_h1_tags(h1_tags):
    if not h1_tags:
        return "No H1 tags found."
    return "\n".join(f" - {tag}" for tag in h1_tags)