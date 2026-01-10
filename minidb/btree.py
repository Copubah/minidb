"""B-Tree implementation for database indexing."""

class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []
        self.values = []  # Row IDs for leaf nodes
        self.children = []
        self.leaf = leaf

class BTree:
    """Simple B-Tree for indexing. Stores key -> set of row_ids."""
    
    def __init__(self, order=4):
        self.root = BTreeNode()
        self.order = order  # Max children per node
    
    def insert(self, key, row_id):
        """Insert a key-rowid pair into the index."""
        root = self.root
        if len(root.keys) == self.order - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, row_id)
    
    def _insert_non_full(self, node, key, row_id):
        i = len(node.keys) - 1
        if node.leaf:
            # Find position and insert
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if i < len(node.keys) and node.keys[i] == key:
                # Key exists, add row_id to set
                node.values[i].add(row_id)
            else:
                node.keys.insert(i, key)
                node.values.insert(i, {row_id})
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == self.order - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, row_id)

    def _split_child(self, parent, i):
        order = self.order
        child = parent.children[i]
        mid = order // 2
        
        new_node = BTreeNode(leaf=child.leaf)
        new_node.keys = child.keys[mid + 1:]
        new_node.values = child.values[mid + 1:]
        
        if not child.leaf:
            new_node.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]
        
        parent.keys.insert(i, child.keys[mid])
        parent.values.insert(i, child.values[mid])
        parent.children.insert(i + 1, new_node)
        
        child.keys = child.keys[:mid]
        child.values = child.values[:mid]
    
    def search(self, key):
        """Search for a key and return set of row_ids."""
        return self._search(self.root, key)
    
    def _search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i].copy()
        if node.leaf:
            return set()
        return self._search(node.children[i], key)
    
    def delete(self, key, row_id):
        """Remove a row_id from a key's set."""
        self._delete(self.root, key, row_id)
    
    def _delete(self, node, key, row_id):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            if row_id in node.values[i]:
                node.values[i].discard(row_id)
                if not node.values[i]:
                    node.keys.pop(i)
                    node.values.pop(i)
            return
        if not node.leaf:
            self._delete(node.children[i], key, row_id)
    
    def all_entries(self):
        """Return all (key, row_ids) pairs."""
        result = []
        self._collect(self.root, result)
        return result
    
    def _collect(self, node, result):
        for i, key in enumerate(node.keys):
            if node.leaf:
                result.append((key, node.values[i].copy()))
        if not node.leaf:
            for child in node.children:
                self._collect(child, result)
