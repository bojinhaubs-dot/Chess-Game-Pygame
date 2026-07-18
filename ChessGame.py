# import dependencies
import pygame as p
import ChessEngine

# set global varieble
WIDTH = HEIGHT = 512
DIMENSIONS = 8
SQ_SIZE = HEIGHT// DIMENSIONS
MAX_FPS = 15
IMAGES = {}

# set frame icon & caption
icon = p.image.load("images\icon.ico")
p.display.set_icon(icon)

p.display.set_caption("Chess Game")

# load imgs from file to pygame.img object
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK' ]
    for piece in pieces: 
        # shrink picture size to fit chess board
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    # initiate pygame window
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    # initiate primary logical object
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    # initiate resources
    loadImages()
    # initiate scoop variebles
    moveMade = False    # 
    animate = False
    running = True      # 
    sqSelected = ()
    playerClicks = []
    gameOver = False
    # initiate loop
    while running: 
        # 1. User's action -> Change objects, variables, indicators
        for e in p.event.get():
            # listen to quit
            if e.type == p.QUIT:
                running = False
            # listen to click
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    # get click position
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    
                    # check: cancle or move
                    if sqSelected == (row, col): # if clicked in the same position, cancel selection
                        sqSelected = ()
                        playerClicks = []
                    else:                        # if clicked in new position, record selection
                        sqSelected = (row, col) 
                        playerClicks.append(sqSelected)

                    # check: invalid start
                    if len(playerClicks) == 1 and (gs.board[row][col] == "--"): # if start in an empty position, cancel collection
                        sqSelected = ()
                        playerClicks = []

                    # check: valid move
                    if len(playerClicks) == 2:                                  # if end in an new position, check if the move is valid  
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)        # if valid, register the move
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(move) # back-end
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:                                                            # if invalid, make the end as start position
                            playerClicks = [sqSelected]
            # listen to keyboard
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False #!
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        
        # 2. render according to changes
        if moveMade:
            if animate:
                animatedMoves(gs.moveLog[-1], screen, gs.board,clock) 
            # reset validMoves
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        drawGameState(screen, gs, validMoves, sqSelected) # ??
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver =True
            drawText(screen, 'Stalemate');
        clock.tick(MAX_FPS) # restrain refreshing rate
        p.display.flip() # update


# static renders
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE)) # add as layer
            s.set_alpha(100) # set transparency
            s.fill(p.Color('blue')) # ??
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE)) # blue the selected start square
            s.fill(p.Color("yellow")) 
            for moves in validMoves:               # yellow the available ends square
                if moves.startRow == r and moves.startCol == c:
                    screen.blit(s, (SQ_SIZE*moves.endCol, SQ_SIZE*moves.endRow))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # base
    highlightSquares(screen, gs, validMoves, sqSelected) # middle
    drawPieces(screen, gs.board) # top

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# serial render
def animatedMoves(move, screen, board, clock):
    global colors
    # calculate total frames
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    # render by frame staticly
    for frame in range(frameCount + 1):
        r,c =((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        # render the base
        drawBoard(screen)
        drawPieces(screen, board)
        # make a cover square
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # render captured piece
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # render the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        # update screen
        p.display.flip()
        clock.tick(60) # restrain refreshing rate

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, True, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2) # center text to the screen
    screen.blit(textObject, textLocation)
    textObject = font.render(text, True, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2,2))


if __name__ == "__main__":
    main()
