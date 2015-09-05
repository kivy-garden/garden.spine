# coding=utf-8

import spine
from spine.SkeletonJson import SkeletonJson
from os.path import dirname, join, realpath
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import (StringProperty, ListProperty, BooleanProperty,
                             OptionProperty)
from kivy.clock import Clock
from kivy.graphics import Color, Mesh, PushMatrix, PopMatrix, Canvas


class AtlasPage(spine.AtlasPage):
    def __init__(self):
        super(AtlasPage, self).__init__()
        self.texture = None


class AtlasRegion(spine.AtlasRegion):
    def __init__(self):
        super(AtlasRegion, self).__init__()
        self.page = None


class Atlas(spine.Atlas):
    def __init__(self, filename):
        self.atlas_dir = dirname(filename)
        super(Atlas, self).__init__()
        super(Atlas, self).loadWithFile(filename)

    def newAtlasPage(self, name):
        page = AtlasPage()
        filename = realpath(join(self.atlas_dir, name))
        if filename:
            page.texture = Image(filename).texture
            page.texture.flip_vertical()
        return page

    def newAtlasRegion(self, page):
        region = AtlasRegion()
        region.page = page
        return region

    def findRegion(self, name):
        return super(Atlas, self).findRegion(name)


class RegionAttachment(spine.RegionAttachment):
    def __init__(self, region):
        super(RegionAttachment, self).__init__()
        self.texture = region.page.texture.get_region(
            region.x, region.y, region.width, region.height)
        u, v = self.texture.uvpos
        uw, vh = self.texture.uvsize
        self.u = u
        self.v = v
        self.u2 = u + uw
        self.v2 = v + vh
        self.first_time = True
        if region.rotate:
            self._tex_coords = (
                self.u2,  # self.vertices[0].texCoords.x
                self.v2,  # self.vertices[0].texCoords.y
                self.u,  # self.vertices[1].texCoords.x
                self.v2,  # self.vertices[1].texCoords.y
                self.u,  # self.vertices[2].texCoords.x
                self.v,  # self.vertices[2].texCoords.y
                self.u2,  # self.vertices[3].texCoords.x
                self.v,  # self.vertices[3].texCoords.y
            )
        else:
            self._tex_coords = (
                self.u,  # self.vertices[0].texCoords.x
                self.v2,  # self.vertices[0].texCoords.y
                self.u,  # self.vertices[1].texCoords.x
                self.v,  # self.vertices[1].texCoords.y
                self.u2,  # self.vertices[2].texCoords.x
                self.v,  # self.vertices[2].texCoords.y
                self.u2,  # self.vertices[3].texCoords.x
                self.v2  # self.vertices[3].texCoords.y
            )

    def prepare_graphics(self, canvas):
        self._mesh_vertices = vertices = [0] * 16
        vertices[2::4] = self._tex_coords[::2]
        vertices[3::4] = self._tex_coords[1::2]
        self.canvas = Canvas()
        with self.canvas:
            Color(1, 1, 1, 1)
            PushMatrix()
            self.g_mesh = Mesh(vertices=vertices,
                               indices=range(4),
                               mode="triangle_fan",
                               texture=self.texture)
            self.g_debug_color = Color(1, 0, 0, 1)
            self.g_debug_mesh = Mesh(vertices=vertices,
                                     indices=range(4),
                                     mode="line_loop", )
            PopMatrix()

    def draw(self, slot, canvas):
        if self.first_time:
            self.first_time = False
            self.prepare_graphics(canvas)

        skeleton = slot.skeleton
        canvas.add(self.canvas)
        """
        # FIXME implement color per vertices (need a global shader for that)
        r = skeleton.r * slot.r * 255.0
        g = skeleton.g * slot.g * 255.0
        b = skeleton.b * slot.b * 255.0
        a = skeleton.a * slot.a * 255.0

        self.vertices[0].color.r = r
        self.vertices[0].color.g = g
        self.vertices[0].color.b = b
        self.vertices[0].color.a = a
        self.vertices[1].color.r = r
        self.vertices[1].color.g = g
        self.vertices[1].color.b = b
        self.vertices[1].color.a = a
        self.vertices[2].color.r = r
        self.vertices[2].color.g = g
        self.vertices[2].color.b = b
        self.vertices[2].color.a = a
        self.vertices[3].color.r = r
        self.vertices[3].color.g = g
        self.vertices[3].color.b = b
        self.vertices[3].color.a = a
        """

        self.updateOffset()
        self.updateWorldVertices(slot.bone)

        # update graphics
        self.g_mesh.vertices = self._mesh_vertices
        if self.debug:
            self.g_debug_mesh.vertices = self._mesh_vertices
            self.g_debug_color.a = 1
        else:
            self.g_debug_color.a = 0

    def updateWorldVertices(self, bone):
        x = bone.worldX
        y = bone.worldY
        m00 = bone.m00
        m01 = bone.m01
        m10 = bone.m10
        m11 = bone.m11
        offset = self.offset
        v = self._mesh_vertices
        v[0::4] = [
            offset[0] * m00 + offset[1] * m01 + x,
            offset[2] * m00 + offset[3] * m01 + x,
            offset[4] * m00 + offset[5] * m01 + x,
            offset[6] * m00 + offset[7] * m01 + x
        ]
        v[1::4] = [
            offset[0] * m10 + offset[1] * m11 + y,
            offset[2] * m10 + offset[3] * m11 + y,
            offset[4] * m10 + offset[5] * m11 + y,
            offset[6] * m10 + offset[7] * m11 + y
        ]


class AtlasAttachmentLoader(spine.AttachmentLoader.AttachmentLoader):
    def __init__(self, atlas):
        super(AtlasAttachmentLoader, self).__init__()
        self.atlas = atlas

    def newAttachment(self, tp, name):
        if tp == spine.AttachmentLoader.AttachmentType.region:
            region = self.atlas.findRegion(name)
            if not region:
                raise Exception("Atlas region not found: %s" % name)
            return RegionAttachment(region)
        else:
            raise Exception('Unknown attachment type: %s' % type)


class Circle(object):
    def __init__(self, x, y, r):
        super(Circle, self).__init__()
        self.x = x
        self.y = y
        self.r = r
        self.color = (0, 255, 0, 255)


class Line(object):
    def __init__(self, length):
        super(Line, self).__init__()
        self.x = 0.0
        self.y = 0.0
        self.x1 = 0.0
        self.x2 = 0.0
        self.length = length
        self.rotation = 0.0
        self.color = (255, 0, 0, 255)
        self.texture = pygame.Surface((640, 480), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.texture, (255, 255, 0, 64),
                         (0, 0, self.texture.get_width(),
                          self.texture.get_height()), 1)

    def rotate(self):
        return pygame.transform.rotozoom(self.texture, self.rotation,
                                         self.xScale)


class Skeleton(spine.Skeleton):
    def __init__(self, skeletonData):
        super(Skeleton, self).__init__(skeletonData=skeletonData)
        self.x = 0
        self.y = 0
        self.texture = None
        self.debug = False
        self.images = []
        self.clock = None

    def draw(self, canvas):
        canvas.clear()
        for slot in self.drawOrder:
            if not slot.attachment:
                continue
            slot.attachment.debug = self.debug
            slot.attachment.draw(slot, canvas)
        """
        if self.debug:
            if not self.clock:
                self.clock = pygame.time.Clock()
            self.clock.tick()
            # Draw the FPS in the bottom right corner.
            pygame.font.init()
            myfont = pygame.font.SysFont(None, 24, bold=True)
            mytext = myfont.render('FPS: %.2f' % self.clock.get_fps(), True,
                                   (255, 255, 255))

            screen.blit(mytext, (screen.get_width() - mytext.get_width(),
                                 screen.get_height() - mytext.get_height()))

            for bone in self.bones:

                if not bone.line:
                    bone.line = Line(bone.data.length)
                bone.line.x = bone.worldX + self.x
                bone.line.y = -bone.worldY + self.y
                bone.line.rotation = -bone.worldRotation
                bone.line.color = (255, 0, 0)

                if self.flipX:
                    bone.line.xScale = -1
                    bone.line.rotation = -bone.line.rotation
                else:
                    bone.line.xScale = 1
                if self.flipY:
                    bone.line.yScale = -1
                    bone.line.rotation = -bone.line.rotation
                else:
                    bone.line.yScale = 1

                bone.line.x1 = bone.line.x + math.cos(
                    math.radians(bone.line.rotation)) * bone.line.length
                bone.line.y1 = bone.line.y + math.sin(
                    math.radians(bone.line.rotation)) * bone.line.length

                pygame.draw.line(screen, bone.line.color,
                                 (bone.line.x, bone.line.y),
                                 (bone.line.x1, bone.line.y1))

                if not bone.circle:
                    bone.circle = Circle(0, 0, 3)
                bone.circle.x = int(bone.worldX) + self.x
                bone.circle.y = -int(bone.worldY) + self.y
                bone.circle.color = (0, 255, 0)

                if 'top left' in bone.data.name:
                    bone.circle.color = (255, 0, 0)
                if 'top right' in bone.data.name:
                    bone.circle.color = (255, 140, 0)
                if 'bottom right' in bone.data.name:
                    bone.circle.color = (255, 255, 0)
                if 'bottom left' in bone.data.name:
                    bone.circle.color = (199, 21, 133)

                pygame.draw.circle(screen, bone.circle.color,
                                   (bone.circle.x, bone.circle.y),
                                   bone.circle.r, 0)
        """


class SpineAsset(Widget):
    filename = StringProperty()
    animations = ListProperty([])
    debug = BooleanProperty(False)
    valign = OptionProperty("middle", options=("bottom", "middle"))

    def __init__(self, **kwargs):
        self.canvas = Canvas()
        super(SpineAsset, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 0)

    def on_filename(self, *args):
        self.load_spine_asset(self.filename)
        self.canvas.clear()
        self.animations = [animation.name
                           for animation in self.skeletonData.animations]
        self.animate(self.animations[0])

    def on_debug(self, *args):
        self.skeleton.debug = self.debug

    def load_spine_asset(self, basefn):
        atlas = Atlas(filename="{}.atlas".format(basefn))
        loader = AtlasAttachmentLoader(atlas)
        skeletonJson = SkeletonJson(loader)
        self.skeletonData = skeletonJson.readSkeletonDataFile(
            "{}.json".format(basefn))
        self.skeleton = Skeleton(skeletonData=self.skeletonData)
        self.skeleton.debug = False
        self.animation = None

    def animate(self, name):
        self.animation = self.skeletonData.findAnimation(name)
        skeleton = self.skeleton

        skeleton.setToBindPose()
        skeleton.flipX = False
        skeleton.flipY = False
        skeleton.updateWorldTransform()

    def update(self, dt):
        if self.animation:
            self.animation.apply(skeleton=self.skeleton,
                                 time=Clock.get_time() / 2.,
                                 loop=True)
        self.skeleton.updateWorldTransform()
        self.skeleton.draw(self.canvas)


Builder.load_string("""
<SpineAsset>:
    canvas.before:
        PushMatrix
        Translate:
            xy: self.center if self.valign == "middle" else (self.center_x, self.y)
    canvas.after:
        PopMatrix
""")
