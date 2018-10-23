while true; do
	timeout 1800 python3 ruwiktionary.py
	echo NEW
	echo "new" >> logs.txt
	sleep 300
	#exit
done

