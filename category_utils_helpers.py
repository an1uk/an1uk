"""
Helper module for processing eBay category subtree JSON.
Provides a function to flatten the nested category tree into a list of tuples.
Fixed to skip nodes missing categoryId.
"""

def flatten_category_tree(node, parent_id=None, path=None):
    """
    Yield tuples for each category in the subtree:
      (category_id, category_name, parent_id, full_path)

    - node: dict with keys 'category' and optionally 'childCategoryTreeNodes'
    - parent_id: ID of the parent category (None for root)
    - path: list of ancestor category names
    """
    if path is None:
        path = []

    cat_info = node.get('category', {})
    cat_id_str = cat_info.get('categoryId')
    cat_name = cat_info.get('categoryName')

    # If no valid categoryId or name, skip yielding this node
    if not cat_id_str or not cat_name:
        # still recurse into children under same parent/path
        for child in node.get('childCategoryTreeNodes', []):
            yield from flatten_category_tree(child, parent_id, path)
        return

    cat_id = int(cat_id_str)

    # Build full path
    current_path = path + [cat_name]
    full_path = ' > '.join(current_path)

    # Yield current node
    yield (cat_id, cat_name, parent_id, full_path)

    # Recurse into children
    for child in node.get('childCategoryTreeNodes', []):
        yield from flatten_category_tree(child, cat_id, current_path)
