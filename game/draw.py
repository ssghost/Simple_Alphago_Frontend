from PIL import Image, ImageDraw

board = Image.new(mode='RGB', size=(540, 540), color = (255,255,255))
colist = list(range(30,570,60))

draw_board = ImageDraw.Draw(board)
for c in colist:
    draw_board.line([0,c,540,c],fill=(0,0,0),width=2)
    draw_board.line([c,0,c,540],fill=(0,0,0),width=2) 

blackpiece = Image.new(mode='RGBA', size=(60,60))
whitepiece = Image.new(mode='RGBA', size=(60,60))

draw_black = ImageDraw.Draw(blackpiece)
draw_white = ImageDraw.Draw(whitepiece)
draw_black.ellipse([0,0,60,60], fill =(0,0,0), outline=(0,0,0))
draw_white.ellipse([0,0,60,60], fill =(255,255,255), outline=(0,0,0))

empty = Image.new(mode='RGB', size=(60, 60), color = (255,255,255))
draw_empty = ImageDraw.Draw(empty)
draw_empty.line([0,30,60,30],fill=(0,0,0),width=2)
draw_empty.line([30,0,30,60],fill=(0,0,0),width=2) 

board.save('board.png','PNG')
blackpiece.save('blackpiece.png','PNG')
whitepiece.save('whitepiece.png','PNG')
empty.save('empty.png','PNG')


