import fontforge as ffg
import json

generate_glyph_svg = False

if generate_glyph_svg is True:
    jianzi_glyphs = ffg.open('./jianzi-glyph.sfd')

    padding = 20
    max_width = 1000 - padding * 2
    max_height = 1000 - padding * 2

    for glyph in jianzi_glyphs.glyphs():
        unicode = glyph.unicode
        xmin, ymin, xmax, ymax = glyph.boundingBox()
        scale_x = max_width / (xmax - xmin)
        scale_y = max_height / (ymax - ymin)
        min_scale = min(scale_x, scale_y)
        glyph.transform((min_scale, 0, 0, min_scale, 0, 0))  # scaleX, skewX, skewY, scaleY, positionX, positionY
        xmin, ymin, xmax, ymax = glyph.boundingBox()
        offset_x = (max_width + padding * 2 - xmax - xmin) / 2
        offset_y = (max_height + padding * 2 - ymax - ymin) / 2 - 120
        glyph.transform((1, 0, 0, 1, offset_x, offset_y))
        glyph.export(f'./glyph_svg/{unicode}.svg')
    
    jianzi_glyphs.close()


jianzi_font = ffg.font()
jianzi_font.encoding = 'UnicodeBMP'
jianzi_font.fontname = 'jianzi-font'
jianzi_font.ascent = 880
jianzi_font.descent = 120
jianzi_font.upos = -125
jianzi_font.hasvmetrics = True

# add full-width space
glyph = jianzi_font.createChar(32)
glyph.width = 1000
glyph.vwidth = 1000

# add spaces of different widths
for i in range(1, 20):
    width = i * 100
    unicode = int("E000", 16) + i
    glyph = jianzi_font.createChar(unicode)
    glyph.width = 1000
    glyph.vwidth = width

def traverse_glyphs(glyphMap):
    if isinstance(glyphMap, dict):
        if 'glyphs' in glyphMap:
            x_pos = glyphMap['x']
            y_pos = glyphMap['y']
            width = glyphMap['width']
            height = glyphMap['height']
            for glyph in glyphMap['glyphs']:
                # add glyph to jianzi_font
                temp_glyph = jianzi_font.createChar(int(glyph['unicode']))
                temp_glyph.clear()
                temp_glyph.importOutlines(f'./glyph_svg/{glyph["filename"]}.svg')
                xmin, ymin, xmax, ymax = temp_glyph.boundingBox()
                scale_x = width / (xmax - xmin)
                scale_y = height / (ymax - ymin)
                if scale_x > 1:
                    scale_x = 1
                if scale_y > 1:
                    scale_y = 1
                offset_x = x_pos + width / 2 - (xmax + xmin) / 2 * scale_x
                offset_y = y_pos + height / 2 - (ymax + ymin) / 2 * scale_y - 120
                temp_glyph.transform((scale_x, 0, 0, scale_y, offset_x, offset_y))  # scaleX, skewX, skewY, scaleY, positionX, positionY
                temp_glyph.width = 1000
                temp_glyph.vwidth = 0
                temp_glyph.removeOverlap()
                temp_glyph.addExtrema()
        else:
            for value in glyphMap.values():
                traverse_glyphs(value)


with open('./jianziMap.json', encoding='utf-8') as f:
    jianziMap = json.load(f)
    traverse_glyphs(jianziMap)


jianzi_font.save('../dist/jianzi-font.sfd')
jianzi_font.generate('../dist/jianzi-font.otf')
jianzi_font.close()