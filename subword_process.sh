subword-nmt learn-bpe -s 2 < ./data/processed/third_step.txt > ./data/processed/fourth_step.txt
subword-nmt apply-bpe -c ./data/processed/fourth_step.txt < ./data/processed/fourth_step.txt > ./data/processed/fifth_step.txt