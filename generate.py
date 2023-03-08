import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            cp = self.domains[var].copy()
            for word in cp:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if not overlap:
            return False
        revision = False
        cp = self.domains[x].copy()
        for x_value in cp:
            match_found = False
            for y_value in self.domains[y]:
                if x_value[overlap[0]] == y_value[overlap[1]]:
                    match_found = True
                    break
            if not match_found:
                self.domains[x].remove(x_value)
                revision = True
        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs:
            que = arcs.copy()
            while len(que) != 0:
                current = que.pop(0)
                if self.revise(*current):
                    que += [(x, current[0]) for x in self.crossword.neighbors(current[0]).remove(current[1])]
                if not self.domains[current[0]]:
                    return False
            return True
        else:
            que = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    que.append((x,y))
            while len(que) != 0:
                current = que.pop(0)
                if self.revise(*current):
                    if self.crossword.neighbors(current[0]) - {current[1]}:
                        que += [(x, current[0]) for x in self.crossword.neighbors(current[0]) - {current[1]}]
                    if len(self.domains[current[0]]) == 0:
                        return False
            return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) != len(self.crossword.variables):
            return False
        else:
            return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            if len(assignment[var]) != var.length:
                return False
            for var2 in assignment:
                if var == var2:
                    continue
                if not self.crossword.overlaps[var, var2]:
                    continue
                overlap = self.crossword.overlaps[var, var2]
                if not (assignment[var][overlap[0]] == assignment[var2][overlap[1]]):
                    return False
        if len(assignment.values()) != len(set(assignment.values())):
            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        constraining_count = { word : 0 for word in self.domains[var]}
        vars_2check = [x for x in self.crossword.neighbors(var) if x not in assignment.keys()]
        for word in self.domains[var]:
            for neighbor in vars_2check:
                overlap = self.crossword.overlaps[var, neighbor]
                for cand in self.domains[neighbor]:
                    if word[overlap[0]] != cand[overlap[1]]:
                        constraining_count[word] += 1
        sorted = dict(sorted(constraining_count.items(), key=lambda item: item[1]))
        return sorted.keys()

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unass = self.crossword.variables - set(assignment.keys())
        remaining_count = {}
        minim = 10000
        for var in unass:
            amt = len(self.domains[var])
            remaining_count.update({var:amt})
            if amt < minim:
                minim = amt
        cands = list()
        for var in remaining_count:
            if remaining_count[var] == minim:
                cands.append(var)
        if len(cands) == 1:
            return cands[0]
        else:
            degrees = dict()
            maxim = -10000
            for var in cands:
                amt1 = len(self.crossword.neighbors(var))
                degrees.update({var:amt1})
                if amt1 > maxim:
                    maxim = amt1
            for h in degrees:
                if degrees[h] == maxim:
                    return h


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        ass = self.select_unassigned_variable(assignment)
        for value in self.domains[ass]:
            assignment.update({ ass : value })
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
                else:
                    del assignment[ass]
            else:
                del assignment[ass]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
