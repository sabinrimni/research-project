import subword_nmt.learn_bpe as subl
import subword_nmt.apply_bpe as suba

# count the characters around insert and delete within 2 or 3 characters as a context matrix
# original / inflection / operation string / characters / occurrence
# assosciation support