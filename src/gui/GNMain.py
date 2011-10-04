import os, sys, pygame, WIIGUIToolkit
from pygame.locals import *
from WIIGUIToolkit import *

def main():
    pygame.init()
    videoInfo = pygame.display.Info()
    FULL_SCREEN_SIZE = (videoInfo.current_w, videoInfo.current_h)
    screen = pygame.display.set_mode(FULL_SCREEN_SIZE)
    pygame.display.set_caption('Network Game')
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(colors['WHITE'])
    screen.blit(background, (0, 0))
    node = GNode(ctrimg='package.png')
    node.rect.topleft = (0, 0)
    node2 = GNode(text="Ninja",
                              textcolor='WHITE',
                              bgcolor='PURPLE')
    node2.rect.topleft = ((500, 0))
    node3 = GNode(text="42", textcolor='BLACK',
                              bgcolor='PINK')
    node3.rect.topleft = ((0, 500))
    node4 = GNode()
    node4.rect.centerx = FULL_SCREEN_SIZE[0]/2
    node4.rect.centery = FULL_SCREEN_SIZE[1]/2
    edge = GEdges(startpos=(node.rect.centerx,
                                          node.rect.centery),
                                endpos=(node2.rect.centerx,
                                        node2.rect.centery), thickness=8,
                                weight=5)
    edge2 = GEdges(startpos=(node.rect.centerx,
                                           node.rect.centery),
                                 endpos=(node3.rect.centerx,
                                         node3.rect.centery), thickness=8,
                                 weight =15)
    edge3 = GEdges(startpos=(node2.rect.centerx,
                                           node2.rect.centery),
                                 endpos=(node3.rect.centerx,
                                         node3.rect.centery), thickness=5,
                                 weight = 20)

    edgeSprites = pygame.sprite.RenderUpdates(edge, edge2, edge3)
    weightSprites = pygame.sprite.RenderUpdates(edge.weight, edge2.weight, edge3.weight)    
    nodeSprites = pygame.sprite.RenderUpdates(node, node2, node3, node4)
    allsprites = pygame.sprite.LayeredUpdates(edgeSprites, weightSprites, nodeSprites)
    node4.queueUpdate(color1="RED", color2="YELLOW", color3="PURPLE")
    allsprites.draw(background)
    screen.blit(background, (0, 0))
    pygame.display.flip()

    while True:
        for event in pygame.event.get(): 
            if event.type == QUIT:
                 sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                if event.key == K_l:
                    print 'L is pressed'
                    node4.queueUpdate(color1="BLUE", color2="ORANGE")
                    allsprites.draw(background)
                    screen.blit(background, (0, 0))
                    pygame.display.flip()
                if event.key == K_s:
                    print 'S is pressed'
                    node4.queueUpdate(color1="ORANGE", color2="GREEN")
                    allsprites.draw(background)
                    screen.blit(background, (0, 0))
                    pygame.display.flip()
                if event.key == K_n:
                    print 'N is pressed'
                    node4.queueUpdate()
                    allsprites.draw(background)
                    screen.blit(background, (0, 0))
                    pygame.display.flip
                if event.key == K_o:
                    print 'O is pressed'
                    node4.queueUpdate(color1="RED", color2="YELLOW",
                                      color3="PURPLE")
                    allsprites.draw(background)
                    screen.blit(background, (0, 0))
                    pygame.display.flip()
                    
main()
            
        
