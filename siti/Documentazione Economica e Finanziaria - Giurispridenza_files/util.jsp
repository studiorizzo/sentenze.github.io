




function clickIE() {
	var message="";
	if (document.all) {
		(message);
		return false;
	}
}



function clickNS(e) {
	if(document.layers||(document.getElementById&&!document.all)) {
		if(e.which==2||e.which==3) {
			(message);
			return false;
		}
	}
}
	/*if(document.layers){
		document.captureEvents(Event.MOUSEDOWN);document.onmousedown=clickNS;
	}
	else{
		document.onmouseup=clickNS;document.oncontextmenu=clickIE;
	}

	document.oncontextmenu=new Function("return false")*/


function setSelect(ente, select){

	var val = ente.options[ente.selectedIndex].value;
	
	
	if(val != ""){
		select.disabled=true;
	}else{
		select.disabled=false;
	}

}



function Trim(stringa){
   var reTrim=/\s+$|^\s+/g;
   return stringa.replace(reTrim,"");
}

function checkMaxLengthTextArea(textarea, evt, maxLength) { 
  if (textarea.selected && evt.shiftKey) 
    // ignore shift click for select 
    return true; 
  var allowKey = false; 
  if (textarea.selected && textarea.selectedLength > 0) 
    allowKey = true; 
  else { 
    var keyCode = 
      document.layers ? evt.which : evt.keyCode; 
    if (keyCode < 32 && keyCode != 13) 
      allowKey = true; 
    else           
      allowKey = textarea.value.length < maxLength; 
  } 
  textarea.selected = false; 
  return allowKey; 
} 

//-------------------------------------------------------------------------------
// Controlla la correttezza della data e del formato gg/mm/aaaa
// Restituisce true se la data e' corretta; false altrimenti
//-------------------------------------------------------------------------------
function checkData(valore){
	// Controllo che la lunghezza sia corretta
	if (valore.length != 10) {
		return false;
	}

	// Controllo che i separatori ('/') siano corretti
	if (valore.charAt(2) != '/' && valore.charAt(4) != '/') {
		return false;
	}

	// Calcolo i valori di giorno mese e anno
	if (valore.charAt(0) == '0')
		var giorno = valore.charAt(1);
	else
		var giorno = (valore.charAt(0) + valore.charAt(1));

	if (valore.charAt(3) == '0')
		var mese = (valore.charAt(4));
	else
		var mese = (valore.charAt(3) + valore.charAt(4));

	var anno = (valore.charAt(6) + valore.charAt(7) + valore.charAt(8) + valore.charAt(9));

	// Controllo che giorno, mese e anno siano numeri positivi e che il mese non sia superiore a 12
	if (isNaN(parseInt(giorno)) || isNaN(parseInt(mese)) || isNaN(parseInt(anno))) {
		return false;
	}
	
	if (parseInt(giorno) <= 0 || parseInt(mese) <= 0 || parseInt(mese) > 12 || parseInt(anno) <= 0) {
		return false;
	}

	// Controllo se l'anno immesso è bisestile
	var febbr = 0;
    if (((anno % 4 == 0) && (anno % 100 != 0)) || (anno % 400 == 0)) {
		febbr = 29;
    } else { 
		febbr = 28;
    }

	// Calcolo il numero di giorni di ciascun mese
	var nMese = new Array();
	nMese[0] = 31;//Gennaio
	nMese[1] = febbr;//Febbraio
	nMese[2] = 31;//;Marzo
	nMese[3] = 30;//Aprile
	nMese[4] = 31;//Maggio
	nMese[5] = 30;//Giugno
	nMese[6] = 31;//Luglio
	nMese[7] = 31;//Agosto
	nMese[8] = 30;//Settembre
	nMese[9] = 31;//Ottobre
	nMese[10] = 30;//Novembre
	nMese[11] = 31;//Dicembre

	// Controllo che il giorno sia corretto per il mese selezionato
	if (parseInt(giorno) <= parseInt(nMese[parseInt(mese)-1])) {
		return true;
	} else {
		return false;
	}
}

function processFormRicSemplice() {
	var errorMessaggeIniziale = "Sono presenti le seguenti anomalie"+":\n"; 
	var errorMessagge = errorMessaggeIniziale;	
	var fmobj = document.forms[0];
	var anno = Trim(fmobj.anno.value);
	var numero = Trim(fmobj.numero.value);
	var parole = Trim(fmobj.parole.value);
	if(anno.length == 0 && numero.length == 0 && parole.length == 0){
		errorMessagge = errorMessagge + "\t -" + " impossibile eseguire la ricerca, parametri insufficienti"+ ";\n";		
	}	
	if(anno.length != 0 ){
		if(anno.length != 4){
			errorMessagge = errorMessagge + "\t -" + " il campo Anno deve essere di quattro cifre "+ ";\n";			
		}else if (isNaN( anno )){
			errorMessagge = errorMessagge + "\t -" + " il campo Anno deve avere un valore numerico"+ ";\n";			
		}
	}	
	if (errorMessagge != errorMessaggeIniziale) {
				alert(errorMessagge);
				return false;			
   	} 
   	else{ 
   		document.forms[0].submit();
   	}	
}


	function openDoc(idArticolo){   
	   window.open("showDocumentContent.jsp?id="+idArticolo,"","top=0,left=0,width=800,height=680,toolbar=no,directories=no,status=yes,resizable=yes,menubar=no,location=no, scrollbars=yes");       

	}
	//funzione chiamata sull'onclick della pagina successiva nella paginazione
	function submitForm(actionDest){
		document.changePage.action = actionDest;		
		document.changePage.submit();
		
	}
	//funzione chiamata sull'onclick alla i-esima pagina nella paginazione
	function submitFormJump(actionDest, pageDest){
		document.changePage.pageDest.value = pageDest-1;
		submitForm(actionDest);
	}

	function processFormRicAvanzataNormativa(){
	
	 
	   var dataEmissioneDa= creaDataDa(Trim(document.ricercaAvanzataNormativaForm.giornoDataEmissioneDa.value), Trim(document.ricercaAvanzataNormativaForm.meseDataEmissioneDa.value), Trim(document.ricercaAvanzataNormativaForm.annoDataEmissioneDa.value));
	   var dataEmissioneA= creaDataA(Trim(document.ricercaAvanzataNormativaForm.giornoDataEmissioneA.value), Trim(document.ricercaAvanzataNormativaForm.meseDataEmissioneA.value), Trim(document.ricercaAvanzataNormativaForm.annoDataEmissioneA.value));
	   var dataGazzettaDa= creaDataDa(Trim(document.ricercaAvanzataNormativaForm.giornoDataGUDa.value), Trim(document.ricercaAvanzataNormativaForm.meseDataGUDa.value), Trim(document.ricercaAvanzataNormativaForm.annoDataGUDa.value));
	   var dataGazzettaA= creaDataA(Trim(document.ricercaAvanzataNormativaForm.giornoDataGUA.value), Trim(document.ricercaAvanzataNormativaForm.meseDataGUA.value), Trim(document.ricercaAvanzataNormativaForm.annoDataGUA.value));
	   
	  if(Trim(document.ricercaAvanzataNormativaForm.parole.value).length==0 & Trim(document.ricercaAvanzataNormativaForm.tipoEstremiNormativa.value).length==0
	  	& Trim(document.ricercaAvanzataNormativaForm.numero.value).length==0 & dataEmissioneDa==null & dataEmissioneA==null & dataGazzettaDa==null & dataGazzettaA==null &
	   	Trim(document.ricercaAvanzataNormativaForm.ente.value).length==0 & Trim(document.ricercaAvanzataNormativaForm.articolo.value).length==0 & Trim(document.ricercaAvanzataNormativaForm.numArticolo.value).length==0 & Trim(document.ricercaAvanzataNormativaForm.numeroGU.value).length==0 &
	    Trim(document.ricercaAvanzataNormativaForm.materiaFiscale.value).length==0 & Trim(document.ricercaAvanzataNormativaForm.superEnte.value).length==0){
		alert("Occorre compilare almeno un campo");
		return;
	  }
	 
	  if((document.ricercaAvanzataNormativaForm.articolo.value == 'Allegato' | document.ricercaAvanzataNormativaForm.articolo.value == 'Articolo') & (Trim(document.ricercaAvanzataNormativaForm.numero.value).length==0 & document.ricercaAvanzataNormativaForm.tipoEstremiNormativa.value.length==0 & dataEmissioneDa==null & dataEmissioneA==null)){
		alert("selezionando articolo o allegato come Tipo Articolo occorre compilare almeno uno tra i seguenti campi:tipo, numero e data");
		return;
	  }
	  
	  if(Trim(document.ricercaAvanzataNormativaForm.numArticolo.value).length!=0 & Trim(document.ricercaAvanzataNormativaForm.articolo.value).length==0 ){
		alert("Digitando il numero dell'articolo è necessario inserire anche il tipo articolo");
		return;
	  }
	   
	   if(dataEmissioneDa != null){
	      if(!checkData(dataEmissioneDa)){
	      alert("Data emissione non corretta");
	      return;
	      }
	   }
	   if(dataEmissioneA != null){
	      if(!checkData(dataEmissioneA)){
	      alert("Data emissione fino A non corretta");
	      return;
	      }
	   }
	   if(dataGazzettaDa != null){
	      if(!checkData(dataGazzettaDa)){
	      alert("Data pubblicazione non corretta");
	      return;
	      }
	   }
	   if(dataGazzettaA != null){
	      if(!checkData(dataGazzettaA)){
	      alert("Data pubblicazione fine A non corretta");
	      return;
	      }
	   }
	   
	   
	   if(dataEmissioneDa != null && dataEmissioneA !=null){
		   if(!controllaDate(dataEmissioneDa,dataEmissioneA)){
		     alert("La Data Emissione deve essere antecedente alla Data Emissione fino A");
		     return;
		   }
	   }
	  	if(dataGazzettaDa != null && dataGazzettaA !=null){
		   if(!controllaDate(dataGazzettaDa,dataGazzettaA)){
		     alert("La Data Pubblicazione deve essere antecedente alla Data Pubblicazione fino A");
		     return;
		   }
	   	}	
	   	if(isNaN(document.ricercaAvanzataNormativaForm.numeroGU.value)){
	   		 alert("Il campo Numero Gazzetta deve contenere solo caratteri numerici");
		     return;
	   	}
		document.ricercaAvanzataNormativaForm.submit();
	}

	function creaDataDa(giorno, mese, anno){
		var dataDa;
		if(anno.length!=0 && !isNaN(anno)){
			if(giorno.length==0 || isNaN(giorno)){
			  giorno = '01';	
			}else if(giorno.length==1){
			      giorno = '0'+giorno;	
			}
			if(mese.length==0 || isNaN(mese)){
			  mese = '01';	
			}else if(giorno.length==1){
			      mese = '0'+mese;	
			}
			if(anno.length!=4){
				for(i=1;i<4-anno.length;i++){
				    anno = '0'+anno;
				}      
			}	
			data= giorno+"/"+mese+"/"+anno;
			return data; 
		}
		else{
		   return null;
		}		
	}	

	function creaDataA(giorno, mese, anno){
		var dataDa;
		if(anno.length!=0 && !isNaN(anno)){
			if(giorno.length==0 || isNaN(giorno)){
			  giorno = '31';	
			}else if(giorno.length==1){
			      giorno = '0'+giorno;	
			}
			if(mese.length==0 || isNaN(mese)){
			  mese = 12;	
			}else if(giorno.length==1){
			      mese = '0'+mese;	
			}
			if(anno.length!=4){
				for(i=1;i<4-anno.length;i++){
				    anno = '0'+anno;
				}      
			}	
			data= giorno+"/"+mese+"/"+anno;
			return data; 
		}
		else{
		   return null;
		}		
	}	

function ripristinaRicAvanzataNormativa(){
	document.ricercaAvanzataNormativaForm.reset();
		
	}	
	
	
	function submitChangeMatFiscaleNormativa(actionDest){		
		$("#formRicAvanzN").get(0).setAttribute('action', actionDest); 
		$("#formRicAvanzN").get(0).setAttribute('js_enabled', 1); 
		$("#formRicAvanzN").submit();
		
		/*
		document.ricercaAvanzataNormativaForm.js_enabled.value=1;		
		document.ricercaAvanzataNormativaForm.action=actionDest;		
		document.ricercaAvanzataNormativaForm.submit();*/
	}

	
	function submitChangeMatFiscalePrassi(actionDest){
		$("#formRicAvanzP").get(0).setAttribute('action', actionDest); 
		$("#formRicAvanzP").get(0).setAttribute('js_enabled', 1); 
		$("#formRicAvanzP").submit();
	
		/*document.ricercaAvanzataPrassiForm.js_enabled.value=1;
		document.ricercaAvanzataPrassiForm.action=actionDest;		
		document.ricercaAvanzataPrassiForm.submit();*/
	}
	
	function submitChangeMatFiscaleGiurisprudenza(actionDest){
		$("#formRicAvanzG").get(0).setAttribute('action', actionDest); 
		$("#formRicAvanzG").get(0).setAttribute('js_enabled', 1); 
		$("#formRicAvanzG").submit();	
	    /*document.ricercaAvanzataGiurisprudenzaForm.js_enabled.value=1;
		document.ricercaAvanzataGiurisprudenzaForm.action=actionDest;		
		document.ricercaAvanzataGiurisprudenzaForm.submit();*/
	}
	
	function submitChangeMatFiscaleRicerca(actionDest){	
	    document.ricercaClassificazioniForm.js_enabled.value=1;
		document.ricercaClassificazioniForm.action=actionDest;		
		document.ricercaClassificazioniForm.submit();
	}
	
	
	function processFormRicAvanzataPrassi(){
	   var dataEmissioneDa= creaDataDa(Trim(document.ricercaAvanzataPrassiForm.giornoDataEmissioneDa.value), Trim(document.ricercaAvanzataPrassiForm.meseDataEmissioneDa.value), Trim(document.ricercaAvanzataPrassiForm.annoDataEmissioneDa.value));
	   var dataEmissioneA= creaDataA(Trim(document.ricercaAvanzataPrassiForm.giornoDataEmissioneA.value), Trim(document.ricercaAvanzataPrassiForm.meseDataEmissioneA.value), Trim(document.ricercaAvanzataPrassiForm.annoDataEmissioneA.value));
	  
	   if(dataEmissioneDa != null){
	      if(!checkData(dataEmissioneDa)){
	      alert("Data emissione non corretta");
	      return;
	      }
	   }
	   if(dataEmissioneA != null){
	      if(!checkData(dataEmissioneA)){
	      alert("Data emissione fino A non corretta");
	      return;
	      }
	   }
	   
	   if(dataEmissioneDa != null && dataEmissioneA !=null){
		   if(!controllaDate(dataEmissioneDa,dataEmissioneA)){
		     alert("La Data Emissione deve essere antecedente alla Data Emissione fino A");
		     return;
		   }
	   }
	   
	   
	   if(Trim(document.ricercaAvanzataPrassiForm.parole.value).length==0 & Trim(document.ricercaAvanzataPrassiForm.tipoEstremiPrassi.value).length==0
	  	& Trim(document.ricercaAvanzataPrassiForm.numero.value).length==0 & dataEmissioneDa==null & dataEmissioneA==null &
	   	Trim(document.ricercaAvanzataPrassiForm.ente.value).length==0 & Trim(document.ricercaAvanzataPrassiForm.materiaFiscale.value).length==0 & 
	   	Trim(document.ricercaAvanzataPrassiForm.superEnte.value).length==0){
		alert("Occorre compilare almeno un campo");
		return;
	  }
	 
	 	document.ricercaAvanzataPrassiForm.submit();
	}

function ripristinaRicAvanzataPrassi(){
	document.ricercaAvanzataPrassiForm.reset();
		
	}	
	
	
	function ripristinaRicAvanzataGiurisprudenza(){
	document.ricercaAvanzataGiurisprudenzaForm.reset();
		
	}
	
	
	function processFormRicAvanzataGiurisprudenza(){
		var dataEmissioneDa= creaDataDa(Trim(document.ricercaAvanzataGiurisprudenzaForm.giornoDataEmissioneDa.value), Trim(document.ricercaAvanzataGiurisprudenzaForm.meseDataEmissioneDa.value), Trim(document.ricercaAvanzataGiurisprudenzaForm.annoDataEmissioneDa.value));
		var dataEmissioneA= creaDataA(Trim(document.ricercaAvanzataGiurisprudenzaForm.giornoDataEmissioneA.value), Trim(document.ricercaAvanzataGiurisprudenzaForm.meseDataEmissioneA.value), Trim(document.ricercaAvanzataGiurisprudenzaForm.annoDataEmissioneA.value));
		   
		if(dataEmissioneDa != null){
	      if(!checkData(dataEmissioneDa)){
	      alert("Data emissione non corretta");
	      return;
	      }
	   	}
	   	if(dataEmissioneA != null){
	      if(!checkData(dataEmissioneA)){
	      alert("Data emissione fino A non corretta");
	      return;
	      }
	   	}	   
		   
		   if(dataEmissioneDa != null && dataEmissioneA !=null){
			   if(!controllaDate(dataEmissioneDa,dataEmissioneA)){
			     alert("La Data Emissione deve essere antecedente alla Data Emissione fino A");
			     return;
			   }
		   }
			
		  if(Trim(document.ricercaAvanzataGiurisprudenzaForm.parole.value).length==0 & Trim(document.ricercaAvanzataGiurisprudenzaForm.tipoEstremiGiurisprudenza.value).length==0
		  	& Trim(document.ricercaAvanzataGiurisprudenzaForm.numero.value).length==0 & dataEmissioneDa==null & dataEmissioneA==null &
		   	Trim(document.ricercaAvanzataGiurisprudenzaForm.ente.value).length==0 & Trim(document.ricercaAvanzataGiurisprudenzaForm.materiaFiscale.value).length==0 & 
		   	Trim(document.ricercaAvanzataGiurisprudenzaForm.superEnte.value).length==0){
			alert("Occorre compilare almeno un campo");
			return;
		  }
		
		document.ricercaAvanzataGiurisprudenzaForm.submit();
	}
	
	//La prima data dev'essere antecedente alla seconda. Formati gg/mm/aaaa.	
	function controllaDate(dataIn, dataFin){
		   var g_Inizio = Trim(dataIn).substring(0,2);
		   var m_Inizio = Trim(dataIn).substring(3,5);
		   var a_Inizio = Trim(dataIn).substring(6,10);  
		   
		   var g_Fine = Trim(dataFin).substring(0,2);
		   var m_Fine = Trim(dataFin).substring(3,5);
		   var a_Fine = Trim(dataFin).substring(6,10);
		   
		   if(((a_Inizio+m_Inizio+g_Inizio) != 0) & ((g_Fine+m_Fine+a_Fine) != 0)  ){
				       if (parseInt(a_Inizio+m_Inizio+g_Inizio) > parseInt(a_Fine+m_Fine+g_Fine)){			      
						   return(false);
				       }
					   else{
					       return(true);			   
					   }	
		   }
		   else{
		       return(true);
		   }	
	}
	
	function retrieveCount(url)
	{				
	if (window.XMLHttpRequest) 
	{ 
	// Non-IE browsers
				req = new XMLHttpRequest();       
				req.onreadystatechange = processStateChange;
				try {
					 sep="?";
					 if(url.indexOf("?")>=0)
					 	sep="&";	
					 req.open("GET", url+sep+"ms="+new Date().getTime(), true);
					 //req.open("GET", url, true);
				} catch (e) {
					 alert(e);
				}
				req.send(null);
			} else if (window.ActiveXObject) { // IE
			
				 req = new ActiveXObject("Microsoft.XMLHTTP");
				if (req) {
					 req.onreadystatechange = processStateChange;
					 sep="?";
					 if(url.indexOf("?")>=0)
					 	sep="&";	
					 req.open("GET", url+sep+"ms="+new Date().getTime(), true);
					 req.send();
				 }
			}
	  }
	  
	  
function toggleLayer( whichLayer )
{
  var elem, vis;
  if( document.getElementById ) // this is the way the standards work
    elem = document.getElementById( whichLayer );
  else if( document.all ) // this is the way old msie versions work
      elem = document.all[whichLayer];
  else if( document.layers ) // this is the way nn4 works
    elem = document.layers[whichLayer];
  vis = elem.style;
  // if the style.display value is blank we try to figure it out here
  if(vis.display==''&&elem.offsetWidth!=undefined&&elem.offsetHeight!=undefined)
    vis.display = (elem.offsetWidth!=0&&elem.offsetHeight!=0)?'block':'none';
  vis.display = (vis.display==''||vis.display=='block')?'none':'block';
}
function hiddenAfterLoad(whichLayer)
{
   var elem, vis;
  if( document.getElementById ) // this is the way the standards work
    elem = document.getElementById( whichLayer );
  else if( document.all ) // this is the way old msie versions work
      elem = document.all[whichLayer];
  else if( document.layers ) // this is the way nn4 works
    elem = document.layers[whichLayer];
  vis = elem.style;
  vis.display = 'none';
}	  

function getCookieExpiredDate(){
	return getCookieDate(2000,1,1);
}
//-------------------------------------------------
//
//-------------------------------------------------
function getCookieDate(day, month, year){
	var date = new Date();
	if (year!=null){
		date.setFullYear(year);
	}
	if (month!=null){
		date.setMonth(month-1);
	}
	if (day!=null){
		date.setDate(day);
	}
	return date;
}

//-------------------------------------------------
//
//-------------------------------------------------
function setCookie(name, value, day, month, year) {
	document.cookie = name + "=" + escape(value) 
	+ ((day == null && month==null && year==null) ? "" : ("; expires="
	+ getCookieExpiredDate(day,month,year).toGMTString()))
}

//-------------------------------------------------
//
//-------------------------------------------------
function removeCookie(name) {
	setCookie(name,"",-1);
}

//-------------------------------------------------
//
//-------------------------------------------------
function existsCookie(name) {
	return getCookie(name)!=null;
}

//-------------------------------------------------
//
//-------------------------------------------------
function getCookie(name) {
	var search = name + "="
	if (document.cookie.length > 0) { 
		offset = document.cookie.indexOf(search)
		if (offset != -1) {
			offset += search.length
			end = document.cookie.indexOf(";", offset)
			if (end == -1){
				end = document.cookie.length
			}
			return unescape(document.cookie.substring(offset, end))
		}
	}
	return null;
}

	function callGetClassificazioni(materia,ambitoRic){
   			//alert("CodiceMateria: " + materia);
   			//alert(ambitoRic);
			var param = {codiceMateria: materia,ambitoRicerca:ambitoRic};
			$.ajax({ 
				  url: 'getClassificazioni',
				  data: param,
				  dataType: 'json',
				  success: function(listaVociResult) {				  
				  	if(listaVociResult!=null){
				  		 var strList = '<option value="">&nbsp;</option>';
					 	 //alert(JSON.stringify(listaVociResult));		
						 $.each(listaVociResult, function(idx, voce) {
						 	var codiceVoce = voce.codiceClassificazione;
						 	var descrizioneVoce = voce.descrizioneVC;
							strList += '<option value="'+codiceVoce+'">'+descrizioneVoce+'</option>';
 						 });
						 if (listaVociResult.length == 0 ){
						 	$("#classificazione").css('width', '200px')
						 	$("#classificazione").attr('disabled','disabled');
						 }else{
						 	$("#classificazione").removeAttr('disabled');
						 	$("#classificazione").css('width', 'auto');					 	 	
						 }	
						 $("#classificazione").html(strList).text();		 	
						 				 	 
					 }  			   
				  },
				  error:  function(data, status, er){
			          //alert(data+"_"+status+"_"+er);			          
			      }
			});
	}
	
	function setCheckboxPresenzaMassimaValue() {
		if (document.getElementById('ricercaPresenzaMassima')
				&& document.getElementById('ricercaPresenzaMassima').value 
				&& document.getElementById('ricercaPresenzaMassima').value == 'true') {
			document.getElementById('ricercaPresenzaMassima').checked = true;
		} else {
			document.getElementById('ricercaPresenzaMassima').checked = false;
		}
	}
