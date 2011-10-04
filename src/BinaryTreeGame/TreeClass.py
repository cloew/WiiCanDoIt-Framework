from random import *

""" The Tree's nodes class """
class node:
	def __init__(self, value, parent = None, left = None, right = None):
		self.value = value
		self.parent = parent
		self.left = left
		self.right = right

""" The Tree Class """
class Tree:
	""" Builds default tree              """ 
	""" root: the first node in the tree """
	def __init__(self):
		self.root = node(int(random()*25))
	
	""" Checks if an Inserter's move would keep the tree sorted            """
	""" Also, checks if the Inserter's move reaches the bottom of the tree """
	""" Returns the new center that the Inserter will sort from            """
	"""   and a parameter to tell whetehr the value should be inserted     """
	def stillSorted(self, value, center, direction):
		# Check if being sorted wrong
		if value < center.value and direction > 0 :
			return center, False
		elif value > center.value and direction < 0 :
			return center, False
		
		# Check if the value has reached the bottom of the tree
		# If so, return the center, and True
		elif not center.left and direction < 0 :
			return center, True
		elif not center.right and direction > 0 :
			return center, True
		
		# Valid move, but not done inserting               
		# Set the center to whichever node is being moved to
		if direction < 0 :
			center = center.left
		elif direction > 0 :
			center = center.right
		return center, 'Middle'
	
	""" Inserts a value that an Inserter has correctly sorted """
	def insert(self, params):
		# Unload parameters
		value = params[0]
		center = params[1]
		direction = params[2]
		
		# Check which direction the number was inserted and build the node on that side
		if direction < 0 :
			center.left = node(value, center)
		elif direction > 0 :
			center.right = node(value, center)
			
		return self.root
	
	def rotateRoot(self, params):
		root = params[0]
		direction = params[1]
		if direction < 0 and root.right is not None:
			newRoot = root.right
			newRoot.parent = root.parent
			if newRoot.parent is None:
				self.root = newRoot
			elif newRoot.parent.right == root:
				newRoot.parent.right = newRoot
			elif newRoot.parent.left == root:
				newRoot.parent.left = newRoot
			else:
				print 'this child is not mine!'	
			root.right = newRoot.left
			if root.right is not None:
				root.right.parent = root.right
			newRoot.left = root
			newRoot.left.parent = newRoot
		elif direction > 0 and root.left is not None:
			newRoot = root.left
			newRoot.parent = root.parent
			if newRoot.parent is None:
				self.root = newRoot
			elif newRoot.parent.right == root:
				newRoot.parent.right = newRoot
			elif newRoot.parent.left == root:
				newRoot.parent.left = newRoot
			else:
				print 'This childrenz is not mine'
			root.left = newRoot.right
			if root.left is not None:
				root.left.parent = root
			newRoot.right = root
			newRoot.right.parent = newRoot
		else:
			newRoot = root 
		return newRoot
			
	""" Function that tests whether the tree is balanced                          """
	"""   by checking the depths of leaves on the right and left of a node        """
	""" If there is a difference of more than one between the levels of a         """
	"""   leaf on the left and a leaf on the right, the function returns          """
	"""   that the tree is unbalanced                                             """
	""" Otherwise it returns the combined list of the nodes right and left leaves """
	def checkBalanced(self, root, level):
		# If the left is empty
		if not root.left:
			# Add the level to the list of leftDepths for leaves
			leftDepths = ([level])
		else:
			# Otherwise, check if the left node is Balanced
			leftDepths = self.checkBalanced(root.left, level +1)
			
		# If the right is empty
		if not root.right:
			# Add the level to the list of rightDepths for leaves
			rightDepths = ([level])
		else:
			# Otherwise, check if the right node is Balanced
			rightDepths = self.checkBalanced(root.right, level +1)
		
		# If either side is unbalanced, return unbalanced
		if leftDepths == "Unbalanced" or rightDepths == "Unbalanced" :
			return "Unbalanced"
		
		# Check if there is a difference of more than two
		#   between the right side and left side
		for x in leftDepths:
			for y in rightDepths:
				if abs(x-y) > 1 :
					return "Unbalanced"
		
		# Otherwise, return the combinatiopn of left and right side depths
		#   for use in parent nodes
		return leftDepths + rightDepths
	
	def printTree(self, node):
		if node.left :
			left = node.left.value
		else:
			left = None
		
		if node.right :
			right = node.right.value
		else:
			right = None
			
		print node.value, "left:", left, "right:", right
		if node.left is not None :
			self.printTree(node.left)
		if node.right :
			self.printTree(node.right)
