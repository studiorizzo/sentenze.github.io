// globals
var pageSize = 10; // numero di risultati per pagina
var totResult = 0; 
var numPages = 0;
var pageIndex = 0;
var $risultati;
var totDocs = 0;

// link 
var link_provv_normativa = "getAttoNormativoDetail.do?ACTION=getSommario&id=";//?ACTION=getSommario&id=<id provvedimento>
var link_provv_prassi = "getPrassiDetail.do?id="; //?id=<id del provvedimento>
var link_provv_giurispriudenza = "getGiurisprudenzaDetail.do?id=" //?id=<id del provvedimento>
var link_provv_sentenza = "getSentenzaDetail.do?searchSen=y&id=";//?searchSen=y&id=<id provvedimento>

// link elementi
var link_parte_prassi = "getParteDetailFromResultList.do?"; //?idPrassi=<id provvedimento>&id=<id elemento>
var link_versione_normativa = "getArticoloDetailFromResultList.do?";//?id=<id versione>&codiceOrdinamento=<codice ordinamento>&idAttoNormativo=<id provvedimento>

// N - P - G - S
var tipoRisultato = ''; 

var ulteriori_risultati = false;
var flag_primo_load = true;
 

//var xmlResultTest =	'<risultatiRicerca><sessione \/><contatori><contatoreNormativa>1504<\/contatoreNormativa><contatorePrassi>443<\/contatorePrassi><contatoreGiurisprudenza>655<\/contatoreGiurisprudenza><\/contatori><risultati><Provvedimento idProvvedimento=\"{91F0BA58-5F93-4A5A-9FFF-39A88998F8F1}\"><estremi link=\"true\">Legge del 23\/12\/2009 n. 191<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[ Disposizioni per la formazione del  bilancio  annuale  e  pluriennale  dello Stato (legge finanziaria 2010). (09G0205)                         ]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 302 del 30\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{F7847965-F0A2-4267-9B6D-3739473B7674}\"><estremi link=\"true\">Comunicato del 07\/12\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  25 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 285 del 07\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{441E1CA7-EC1B-4EE3-8F48-C596A96631B6}\"><estremi link=\"true\">Comunicato del 07\/12\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  23 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 285 del 07\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{2A299EF8-9F6B-4905-BDFF-F01664E37729}\"><estremi link=\"true\">Comunicato del 07\/12\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  24 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 285 del 07\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{6E7E5CF5-BD32-4FBE-ACB7-55B2A9047740}\"><estremi link=\"true\">Comunicato del 01\/12\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  19 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 280 del 01\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{67A61384-9179-431A-990B-63BE91E5D559}\"><estremi link=\"true\">Comunicato del 01\/12\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  18 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 280 del 01\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{F81FDE84-FBBB-4625-BCBC-E3D65A367AA0}\"><estremi link=\"true\">Comunicato del 01\/12\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  20 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 280 del 01\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{19ECD5CB-729D-4255-A2C2-D3C418AAF71C}\"><estremi link=\"true\">Comunicato del 30\/11\/2009 - Cassa Depositi e Prestiti<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Avviso  relativo all\'emissione di sei nuove serie di buoni fruttiferi postali]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 279 del 30\/11\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{1AACF160-B494-4DDA-97BE-DD0BF7076D97}\"><estremi link=\"true\">Decreto del 30\/11\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Chiusura  anticipata    della    raccolta    delle   giocate  e   slittamento delle  estrazioni dei   giochi  Lotto  e  Enalotto per le giornate festive di dicembre 2009.]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 284 del 05\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{BF6D1EE3-9468-42EA-BCD8-E016FE7A5E6A}\"><estremi link=\"true\">Comunicato del 28\/11\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Avviso   relativo    dell\'annullamento     di    taluni     biglietti   delle lotterie nazionali ad estrazione istantanea]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 278 del 28\/11\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{18E9B9E6-845A-4DD7-9C04-0A1A02D355EA}\"><estremi link=\"true\">Ordinanza ministeriale del 27\/11\/2009 n. 3825 - Presidenza Consiglio dei Ministri<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Ulteriori  disposizioni  urgenti   di  protezione   civile  per  fronteggiare la   grave  situazione   di   emergenza   determinatasi   a   seguito   delle eccezionali  avversita\' atmosferiche   del  1   ottobre  2009 nel territorio della  provincia di  Messina  e   per  fronteggiare   gli  eventi alluvionali del mese di dicembre 2008. (Ordinanza n. 3825).]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 284 del 05\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{D99606CC-853E-4DCB-90C2-BC5CBD34AF3B}\"><estremi link=\"true\">Ordinanza ministeriale del 27\/11\/2009 n. 3827 - Presidenza Consiglio dei Ministri<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Ulteriori   interventi    urgenti   diretti   a   fronteggiare   gli   eventi sismici  verificatisi nella   regione   Abruzzo   il  giorno  6  aprile  2009 e    altre   disposizioni   di  protezione   civile.  (Ordinanza   n.  3827).]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 284 del 05\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{86DE78C7-0BB0-4518-865F-5A7AE921B65A}\"><estremi link=\"true\">Comunicato del 27\/11\/2009 - Banca d\'Italia<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Guide  pratiche relative ai contratti di conto corrente e di mutui ipotecari.]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 277 del 27\/11\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{6F471776-387B-4074-9B35-FE647CD8861A}\"><estremi link=\"true\">Comunicato del 25\/11\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  17 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 275 del 25\/11\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{1C522892-2808-4A25-B51F-5D2FED0B152F}\"><estremi link=\"true\">Comunicato del 25\/11\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  16 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 275 del 25\/11\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{4306AE16-7EEF-4D78-A11F-E7FE5D562FE6}\"><estremi link=\"true\">Comunicato del 25\/11\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Cambi  di riferimento  rilevati a  titolo indicativo  del giorno  13 novembre 2009]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 275 del 25\/11\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{723A2108-8939-4449-A41B-512F8BC317B9}\"><estremi link=\"true\">Provvedimento del 25\/11\/2009 - Agenzia del Territorio<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Accertamento  del    periodo    di   irregolare   funzionamento  dell\'Agenzia del territorio - Ufficio provinciale di Brescia.]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 282 del 03\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{EE6CCB4E-5038-4C24-A14E-FE29A6E839B1}\"><estremi link=\"true\">Provvedimento del 25\/11\/2009 - Agenzia del Territorio<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Accertamento  del    periodo    di    mancato    funzionamento   dell\'Agenzia del territorio - Ufficio provinciale di Lodi.]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 282 del 03\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{E25FA51B-4576-4B52-8F91-65DC294E11E0}\"><estremi link=\"true\">Ordinanza ministeriale del 25\/11\/2009 n. 3822 - Presidenza Consiglio dei Ministri<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Ulteriori   interventi    urgenti   diretti   a   fronteggiare   gli   eventi sismici  verificatisi nella   regione   Abruzzo   il  giorno  6  aprile  2009 e    altre   disposizioni   di  protezione   civile.  (Ordinanza   n.  3822).]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 284 del 05\/12\/2009<\/datiGU><\/Provvedimento><Provvedimento idProvvedimento=\"{E8AF666B-8C50-4657-A784-A931403B54E4}\"><estremi link=\"true\">Decreto del 24\/11\/2009 - Min. Economia e Finanze<\/estremi><titoliProvvedimento><titoloProvvedimento><![CDATA[Riapertura  delle    operazioni    di    sottoscrizione    dei    buoni   del Tesoro  poliennali 4,25%,   con  godimento   1  settembre   2009 e scadenza 1 marzo 2020, quinta e sesta tranche.]]><\/titoloProvvedimento><\/titoliProvvedimento><datiGU>Pubblicato in Gazzetta Ufficiale n. 282 del 03\/12\/2009<\/datiGU><\/Provvedimento><\/risultati><\/risultatiRicerca>';
//var xmlResultTest = '<?xml version=\"1.0\" encoding=\"UTF-8\"?><risultatiRicerca><contatori><contatoreNormativa>0</contatoreNormativa><contatorePrassi>0</contatorePrassi><contatoreGiurisprudenza>0</contatoreGiurisprudenza></contatori><risultati><Provvedimento/></risultati></risultatiRicerca>';


// nessun risultato
function noResult(){
	$(".risultati-ricerca").html("<div class='risultato-ricerca'>Risultati trovati: 0</div>"); 
	$("#contatoreNormativa").html("(0)");
	$("#contatorePrassi").html("(0)");
	$("#contatoreGiurisprudenza").html("(0)");
	$("#totDocumentiTrovati").html("0"); 
	$(".pagine-ricerca").hide(); // non mostrare i paginatori				
}

//nessun risultato
function noResultFiltered(){
	$(".risultati-ricerca").html("<div class='risultato-ricerca'>Risultati trovati: 0</div>"); 
//	$("#contatoreNormativa").html("(0)");
//	$("#contatorePrassi").html("(0)");
//	$("#contatoreGiurisprudenza").html("(0)");
//	$("#totDocumentiTrovati").html("0"); 
	$(".pagine-ricerca").hide(); // non mostrare i paginatori				
}

// parsing di una pagina di risultati 
function showPageResult(page){  		
	
	
	page.each(function(){ // parse dei provvedimenti
		
		var risultatoHTML = '';  				
		var idProvvedimento = $(this).attr('idProvvedimento');  				
		var $estremi = $(this).find("estremi"); 
		var estremiLinkFlag = $estremi.attr('link');
		var $titoliProvvedimento = $(this).find("titoliProvvedimento");
		var $elementi = $(this).find("elementi");
		var $datiGU = $(this).find("datiGU");
		var $conversione = $(this).find("conversione");
		var $abrogazione = $(this).find("abrogazione");
		var $notaProvvedimento = $(this).find("notaProvvedimento");
		var label = "";
		
		if($estremi && idProvvedimento && estremiLinkFlag){
			if (estremiLinkFlag == "true"){
				
				
				var estremiLink = "";
				
				switch (tipoRisultato) { 

				  case "N": 
					estremiLink = link_provv_normativa + idProvvedimento;
				    break; 

				  case "P": 
					estremiLink = link_provv_prassi + idProvvedimento; 
				    break; 

				  case "G":
					label = "<strong>Intitolazione:</strong><br>";
					estremiLink = link_provv_giurispriudenza + idProvvedimento;
				    break; 
				  
				  case "S":
					label = "<strong>Intitolazione:</strong><br>";
					estremiLink = link_provv_sentenza + idProvvedimento;
				  	break; 

				}
			
				risultatoHTML += '<h3><a href="'+estremiLink+'">'+$.trim($estremi.text())+'</a></h3>';
			}else{
				risultatoHTML += '<h3>'+$.trim($estremi.text())+'</h3>';  
			}
		}
		
		if ($datiGU && $datiGU.text()){
			risultatoHTML += '<p class="isola"><em>'+$.trim($datiGU.text())+'</em></p>'; 
		}
		
		if($titoliProvvedimento){
			$titoliProvvedimento.find("titoloProvvedimento").each(function(){	
				var $titoloProvvedimento = $(this);
				if ($titoloProvvedimento && $titoloProvvedimento.text()){					
					risultatoHTML += '<p>'+label+$.trim($titoloProvvedimento.text())+'</p>';
				}
			});				
		}		

		if ($conversione && $conversione.text()){
			risultatoHTML += '<p>'+$.trim($conversione.text())+'</p>';
		}		
		
		if($abrogazione && $abrogazione.text()){
			risultatoHTML += '<p>'+$.trim($abrogazione.text())+'</p>';
		}		
		 				
		if($notaProvvedimento && $notaProvvedimento.text()){
			risultatoHTML += '<p><strong>Nota: </strong><br>'+$.trim($notaProvvedimento.text())+'</p>';
		}
		
		if($elementi){
			$elementi.find("elemento").each(function(){	
				 var $elemento = $(this);  					 
				 var idElemento = $elemento.attr('idElemento');
				 var tipoElemento = $elemento.attr('tipoElemento');
				 var elementoLinkFlag = $(this).attr('link');
				 var $titoloElemento = $(this).find("titoloElemento");    					 
				 var from_search = "true";
				 var codiceOrdinamento= $(this).attr("codiceOrdinamento");			 
				
				 if (elementoLinkFlag == "true"){  					 	
					 
					 var elementoLink = "";
					 
					 if(tipoRisultato == "N"){
						 elementoLink = link_versione_normativa + "id=" + idElemento 
	 					 + "&codiceOrdinamento=" + codiceOrdinamento 
	 					 + "&idAttoNormativo=" + idProvvedimento; 				 			
				 	 }else if(tipoRisultato == "P"){
				 		elementoLink = link_parte_prassi + "idPrassi=" + idProvvedimento
				 					+ "&id=" + idElemento;
				 	 }			 		

				 	 risultatoHTML += '<p class="bullet"><strong><a href="'+elementoLink+'">'+tipoElemento+'</a></strong></p>';

				 }else{
				 	risultatoHTML += '<p class="bullet"><strong>'+tipoElemento+'</strong></p>';
				 }

				 
				 risultatoHTML += '<p class="ident">'+$.trim($titoloElemento.text())+'</p>';// sintesi per la prassi			
				 
				 var $versioniElemento = $(this).find("versioniElemento");
				 if ($versioniElemento){
					 risultatoHTML += '<ul>';
					 $versioniElemento.find("versioneElemento").each(function(){
					 	var idVersione = $(this).attr('idversione');
					 	var versioneLinkFlag = $(this).attr('link');	   					 	
					 	if(idVersione && versioneLinkFlag){
						 	if(versioneLinkFlag == "true"){
						 		
						 		var versioneLink = link_versione_normativa +"id=" + idVersione 
			 					   					+ "&codiceOrdinamento=" + codiceOrdinamento 
			 					   					+ "&idAttoNormativo=" + idProvvedimento;
						 		
						 		risultatoHTML += '<li><a href="'+versioneLink+'">'+$.trim($(this).text())+'</a></li>';
						 	}else{
						 	    risultatoHTML += '<li>'+$.trim($(this).text())+'</li>';
						 	}
					 	}
					 });
					 risultatoHTML += '</ul>';
				}
			});	
			
		}
		
		// effetto sul reload della pagina
		if(flag_primo_load){
			$(".risultati-ricerca").hide();
			$(".pagine-ricerca").hide();
			$(".risultati-ricerca").append('<div class="risultato-ricerca">' + risultatoHTML + '</div>');
			$(".risultati-ricerca").fadeIn(500);
			$(".pagine-ricerca").fadeIn(500);
			flag_primo_load = false;
		}else{
			$(".risultati-ricerca").append('<div class="risultato-ricerca">' + risultatoHTML + '</div>');
		}
		
	
	}); 				

}

// prende la pagina dei risultati con indice "pageIndex"
function getPage(pageIndex,$r){
	var page;
	var startIndex = (pageIndex - 1) * pageSize; // 0-based
	var endIndex = startIndex + pageSize;	
	if (endIndex < totResult){	
		page = $r.slice( startIndex , endIndex);
	}else{
		page = $r.slice(startIndex); // last page
	}	
	return page;			
}

// mostra i risultati della prima pagina
function showFirstPage(){
	
	if (xmlResult){
		var xmlDoc = $.parseXML(xmlResult);
		var $xml = $(xmlDoc);		
		
		// mostra numero totale di documenti		
		showTotalCounter($xml);		
		
		// mostra suggerimenti
		showSuggestion($xml);
		
		//ulteriori risultati
		$ulteriori_risulati = $xml.find("ulterioriRisultati");
		if ($ulteriori_risulati && $ulteriori_risulati.text()==='true'){
			ulteriori_risultati = true;
		}else{
			ulteriori_risultati = false;
		}
		//alert("ulteriori_risultati: " + ulteriori_risultati);
		
		// mostra risultati
		$risultati = $xml.find("Provvedimento");	
		if($risultati && totDocs>0){
			totResult = $risultati.length;
			//alert("numero di risultati: " + totResult);
			if(totResult>0){				
				// numero di pagine
				// pari al massimo numero di pagine "piene" se ulteriori_risultati == true
				// altrimenti sarà pari al numero di pagine "reali"
				if(ulteriori_risultati){
					numPages = Math.floor(totResult/pageSize);
					//alert("num pagine piene: " + numPages);
				}else{
					numPages = Math.ceil(totResult/pageSize);
					//alert("num pagine reali: " + numPages);
				}				
				
				$(".numPages").html(numPages);
				// indice pagina iniziale da mostrare
				var $pagina = $xml.find("pagina");
				//alert("prima pagina da mostrare: " + numPages);
				var numPagIniziale = parseInt($pagina.text());				
				if ($.isNumeric(numPagIniziale) && numPagIniziale>0){
					pageIndex = numPagIniziale;	
				}else{
					pageIndex = 1;
				}				
				$(".pageIndex").html(pageIndex);
				
				var page = getPage(pageIndex,$risultati);
				showPageResult(page);	
			}else{
				noResultFiltered();
			}		
		
		}
		
		
	}else{			
		noResult();								
	}
}


function gestisciPaginatori(){

	// gestione pulsante carica altri risultati
	$(".ulteriori").hide();
	
	
	
	
	if( numPages <= 1){	// solo una pagina	
		$(".indietro").hide();
		$(".avanti").hide();		
		if($(window).width() < 768){// mobile			
			//$(".pagine-ricerca").css('text-align','center');
			$(".pagine-ricerca").hide();
		}
		// gestione pulsante carica altri risultati
		if(ulteriori_risultati){
			$(".ulteriori").show();
		}		
	}else if(pageIndex == 1){ // prima pagina
		$(".indietro").hide();		
		$(".avanti").show();
		$(".avanti").css('border-left','0px');		
		if($(window).width() < 768){// mobile
			$(".pagine-ricerca").css('text-align','right');
		}
	}else if (pageIndex == numPages){ // ultima pagina
		$(".avanti").hide();
		$(".indietro").show();
		if($(window).width() < 768){// mobile
			$(".pagine-ricerca").css('text-align','left');
		}		
		// gestione pulsante carica altri risultati
		if(ulteriori_risultati){
			$(".ulteriori").show();
		}		
	}else{ // pagina intermedia
		$(".avanti").show();
		if($(window).width() >= 768){// solo nel desktop
			$(".avanti").css('border-left','1px #004B85 solid');
		}		
		$(".indietro").show();		
		if($(window).width() < 768){// mobile
			$(".pagine-ricerca").css('text-align','left');
		}
	}
	
	// scroll to TOP
	$('html, body').animate({
        scrollTop: 0
    }, 0/*800*/);
	
	
}

function showTotalCounter($xml){
	// contatori
	var $contatoreNormativa = $xml.find("contatoreNormativa");
	var $contatorePrassi = $xml.find("contatorePrassi");	
	var $contatoreGiurisprudenza = $xml.find("contatoreGiurisprudenza");  			
	
	
	if ($contatoreNormativa && $contatorePrassi && $contatoreGiurisprudenza){
		$("#contatoreNormativa").html("("+$contatoreNormativa.text()+")");
		$("#contatorePrassi").html("("+$contatorePrassi.text()+")");
		$("#contatoreGiurisprudenza").html("("+$contatoreGiurisprudenza.text()+")");		
		
		var cN = parseInt($contatoreNormativa.text());
		var cP = parseInt($contatorePrassi.text());
		var cG = parseInt($contatoreGiurisprudenza.text())
		
		totDocs = cN + cP + cG;
		
		if ((tipoRisultato == 'N' && cN == 0)||(tipoRisultato == 'P' && cP == 0)||((tipoRisultato == 'G'|| tipoRisultato == 'S')&& cG == 0)){
			$(".risultati-ricerca").html("<div class='risultato-ricerca'>Risultati trovati: 0</div>"); 
			$(".pagine-ricerca").hide(); 
		}			
	}
	
	
	if(totDocs==0){
		noResult();
	}else {
		$("#totDocumentiTrovati").html(totDocs);
	}
	
}

function showSuggestion($xml){
	var $doyoumean = $xml.find("doyoumean");
	if($doyoumean){
		var vociHtml = '';
		$doyoumean.find("voce").each(function(){
			var voce = $(this).text();					
			if (voce){
				vociHtml = vociHtml + '&nbsp;' + '<a href="#" onClick="javascript:submitDoYouMean(\''+voce+'\');">' + voce + '</a>';
			}					
		}); 
		if (vociHtml){
			$("#doyoumean-list").html('Forse cercavi:&nbsp;' + vociHtml);					
		}
	} 
}

