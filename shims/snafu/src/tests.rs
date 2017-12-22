use super::tags::Tag;

#[test]
fn test_tag_parse() {
    let (tag, len) = Tag::parse("3.5");
    assert_eq!(len, 3);
    assert_eq!(tag.to_string(), "3.5");
}

#[test]
fn test_tag_parse_arch() {
    let (tag, len) = Tag::parse("3.5-32");
    assert_eq!(len, 6);
    assert_eq!(tag.to_string(), "3.5-32");
}

#[test]
fn test_tag_parse_python() {
    let (tag, len) = Tag::parse("python3.5");
    assert_eq!(len, 3);
    assert_eq!(tag.to_string(), "3.5");
}

#[test]
fn test_tag_parse_python_arch() {
    let (tag, len) = Tag::parse("python3.5-32");
    assert_eq!(len, 6);
    assert_eq!(tag.to_string(), "3.5-32");
}

#[test]
fn test_tag_parse_python_major() {
    let (tag, len) = Tag::parse("python3");
    assert_eq!(len, 1);
    assert_eq!(tag.to_string(), "3");
}

#[test]
fn test_tag_parse_easy_install() {
    let (tag, len) = Tag::parse("easy_install-3.5");
    assert_eq!(len, 4);
    assert_eq!(tag.to_string(), "3.5");
}

#[test]
fn test_tag_parse_easy_install_arch() {
    let (tag, len) = Tag::parse("easy_install-3.5-32");
    assert_eq!(len, 7);
    assert_eq!(tag.to_string(), "3.5-32");
}

#[test]
fn test_tag_parse_easy_install_major() {
    let (tag, len) = Tag::parse("easy_install-3-32");
    assert_eq!(len, 5);
    assert_eq!(tag.to_string(), "3-32");
}

#[test]
fn test_tag_contains() {
    let lh = Tag::from_name("3");
    let rh = Tag::from_name("3.5");
    assert_eq!(lh.contains(&rh), true);
    assert_eq!(rh.contains(&lh), false);
}

#[test]
fn test_tag_contains_arch() {
    let lh = Tag::from_name("3.5");
    let rh = Tag::from_name("3.5-32");
    assert_eq!(lh.contains(&rh), true);
    assert_eq!(rh.contains(&lh), false);
}
