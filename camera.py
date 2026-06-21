from pygame import Rect


class Camera:
	def __init__(self, width, height, world_width=None, world_height=None):
		self.width = width
		self.height = height
		self.world_width = world_width
		self.world_height = world_height
		self.offset = [0, 0]

	def follow(self, target_rect):
		self.offset[0] = target_rect.centerx - self.width // 2
		self.offset[1] = target_rect.centery - self.height // 2

		if self.world_width is not None:
			self.offset[0] = max(0, min(self.offset[0], self.world_width - self.width))
		else:
			self.offset[0] = max(0, self.offset[0])

		if self.world_height is not None:
			self.offset[1] = max(0, min(self.offset[1], self.world_height - self.height))
		else:
			self.offset[1] = max(0, self.offset[1])

	def apply(self, rect):
		return Rect(rect.x - self.offset[0], rect.y - self.offset[1], rect.width, rect.height)


