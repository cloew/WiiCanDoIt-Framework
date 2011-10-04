
COLORS=red green blue purple cyan
SIZE=128x128
BORDER=50
#SHADE=120x3
SHADE=50x20

PNGS=$(foreach a,${COLORS},grid_${a}.png)

.PHONY: all clean
all:: ${PNGS}

# from http://www.imagemagick.org/Usage/advanced/
${PNGS}: grid_%.png : base.png 
	convert $< -matte \( +clone -channel A -separate +channel -negate \
			-bordercolor black -border ${BORDER}  -blur 0x2 -shade ${SHADE} \
			-normalize -blur 0x1 -fill $* -tint 100 \) \
			-gravity center -compose Atop -composite $@
	
base.png: 
	convert -size ${SIZE} xc:black   $@

clean:
	${RM} *.png *~

