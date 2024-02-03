
	massimi_relativi.log e' la stampa dei massimi relativi che entrano nella funzione detect()
	candidati.log 		--> senza applicare soglie e senza FFT 
	candidati_new.log 	--> senza applicare soglie ma con FFT 
	candidates_th.log	--> applicando soglie e con FFT
	candidates_th_orig.log	--> applicando soglie ma senza FFT 

	new_thresholds.txt e old_thresholds.txt mi sono serviti per fare un confronto tra i risultati ottenuti utlizzando le nuove soglie o le vecchie:
	con le vecchie soglie ci sono piu' casi in cui i fondamentali non trovano il loro pattern (ovviamente) ma le note spurie sono un po' di meno 
	piu' o meno 2 in meno rispetto ai "candidates" quando uso le soglie nuove; comunque pero' ci sono e nella vecchia logica di chitarra pulivo i risultati con 
	altri metodi e con altri passaggi, quindi a livello di soglie non mi conviene riadottare le vecchie, meglio attenersi alle nuove. 

Alla fine decido di applicare FFT e soglie perche' migliora i risultati e comunque mi riduce il numero di candidati rispetto ai massimi relativi (anche se pulisce di
meno rispetto al considerare solo RTFI come avevo previsto in /home/luciamarock/Dropbox/shared/dev/PitchDetector/appunti/guitar/first_condition_detection/readme.txt). 

