
	la funzione analyzer.detect() per ora cerca e si aspetta gli armonici tra gli elementi dei massimi relativi 
	questo non e' sempre vero (consultare output.log per vedere le note su cui questo non e' vero)
	ho graficato tali note a tali istanti e ho visto che effettivamente gli armonici del fondamentale rilevato non sono massimi relativi 
	(questo puo' succedere soprattutto considerando che siamo ai primi istanti)
	ho notato che molte volte liddove RTFI non ha gli arminici della tripletta tra i massimi relativi, FFT incece ce li ha quindi si puo' fare un OR con quelli 
	
	inoltre ci sarebbero da aggiungere altre condizioni sulla det monofonica e su spctral matching
	questo mi serve per limitare i casi in cui una nota e' presente nei massimi relativi ma per mancanza degli armonici atttesi non viene rilevata

	poi c'e' da fare il discorso contrario e cioe' ripulire il vettore dei massimi relativi dai candidati sbagliati (utilizzando le soglie e l'energia minima)
	la correzione menzionata prima potrebbe peggiorare le cose nell'ottica di una "pulizia" dei candidati 
	infatti cosi' e' pero' ho deciso di andare avanti ed affidarmi al calcolo dell'energia minima con la quale discriminare le note spurie, 
		leggere /home/luciamarock/Dropbox/shared/dev/PitchDetector/appunti/guitar/thresholds/readme.txt 

	quindi adesso vado avanti con il calcolo dell'energia minima (essa e' una tecnica applicata al pianorforte che pero' mi funzionava bene)


