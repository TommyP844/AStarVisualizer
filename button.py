
import pygame

class Button(object):
    
    def __init__(self, x, y, width, height, text, fontsize,
                 bgColor, highlight, textColor = (0, 0, 0), highlightColor = (0, 0, 0)):
        self.highlight = highlight
        self.bg = bgColor
        self.highlightColor = highlightColor
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.fontsize = fontsize
        self.font = pygame.font.SysFont(None, fontsize)
        self.textobj = self.font.render(text, True, textColor)

    def draw(self, screen, mouse):

        if (self.isOver(mouse) and self.highlight):
            pygame.draw.rect(screen, self.highlightColor, self.rect)
        else:
            pygame.draw.rect(screen, self.bg, self.rect)

        text_width, text_height = self.textobj.get_width(), self.textobj.get_height()
        textpos = (self.rect.centerx - text_width // 2, self.rect.centery - text_height // 2)
        #
        screen.blit(self.textobj, textpos)

    def isOver(self, pos):
        return self.rect.collidepoint(pos)


