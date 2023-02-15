""" STORES INFORMATION """


class GameState():
    def __init__(self):
        # board is 8x8 2D list, each element of the list has 2 characters
        # The first character represents the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()  # coordinates for the square where an en passant capture is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                             self.currentCastlingRights.bks, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update king location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endColumn)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endColumn)
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + 'Q'

        # en passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endColumn] == '--'
        # update en passant variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:  # only on 2 sq pawn advances
            self.enpassantPossible = (
                (move.startRow + move.endRow) // 2, move.endColumn)  # double divide is integer division
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2:  # kingside
                self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1]
                self.board[move.endRow][move.endColumn + 1] = '--'  # erase old rook
            else:  # queenside
                self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                self.board[move.endRow][move.endColumn - 2] = '--'

        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                                 self.currentCastlingRights.bks, self.currentCastlingRights.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the king location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startColumn)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startColumn)
            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endColumn] = '--'  # leave landing square blank
                self.board[move.startRow][move.endColumn] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endColumn)

            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightsLog.pop()  # get rid of new castle rights from the move we are undoing
            self.currentCastlingRights = self.castleRightsLog[-1]  # set castle rights to the last one in the list
            # undo castle move
            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2:
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 1]
                    self.board[move.endRow][move.endColumn - 1] = '--'
                else:
                    self.board[move.endRow][move.endColumn - 2] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][move.endColumn + 1] = '--'

    '''
    Update the castle rights
    '''

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wqs = False
            self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bqs = False
            self.currentCastlingRights.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startColumn == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startColumn == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startColumn == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startColumn == 7:  # right rook
                    self.currentCastlingRights.bks = False

        if move.pieceCaptured == 'wR':
            if move.endColumn == 0:
                self.currentCastlingRights.wqs = False
            elif move.endColumn == 7:
                self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endColumn == 0:
                self.currentCastlingRights.bqs = False
            elif move.endColumn == 7:
                self.currentCastlingRights.bks = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                        self.currentCastlingRights.bks, self.currentCastlingRights.bqs)
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.whiteKingLocation[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck:
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = False
        self.enpassantPossible = tempEnpassantPossible  # saves the value during move generation
        self.currentCastlingRights = tempCastleRights #copy made to reuse later
        return moves

    def squareUnderAttack(self, r, c):
        """ Determine if enemy can attack the square row and column """
        self.whiteToMove = not self.whiteToMove
        opponentsMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentsMoves:
            if move.endRow == r and move.endColumn == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 1][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endColumn = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endColumn = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endColumn = c + m[1]
            if 0 < endRow < 8 and 0 <= endColumn < 8:
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endColumn), self.board))

    def getKingMoves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

        '''
        Generate all valid castle moves for the king at (r, c) and then add them to the list of moves
        '''

    def getCastleMoves(self, r, c, moves):
        if self.inCheck:
            return  # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) \
                or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) \
                or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves,)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startColumn = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startColumn = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = []
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endColumn = startColumn + d[1] * i
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endPiece = self.board[endRow][endColumn]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endColumn, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endColumn, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endColumn = startColumn + m[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                endPiece = self.board[endRow][endColumn]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endColumn, m[0], m[1]))
        return inCheck, pins, checks


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSQ, endSQ, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSQ[0]
        self.startColumn = startSQ[1]
        self.endRow = endSQ[0]
        self.endColumn = endSQ[1]
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (
                self.pieceMoved == 'bP' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        # castle move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startColumn) + self.getRankFile(self.endRow, self.endColumn)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
