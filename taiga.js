// ==UserScript==
// @name           taiga
// @namespace      *
// @include        http://*.wikipedia.org/*
// ==/UserScript==

//TODO
//añadir a recentchanges una pestaña a newbies y a newpages
//usar cookies para controlar preferencias 
//iluminar las ediciones de ips en RC

// 
// Inicialización de fechas actuales
// 
currentDate=new Date();
currentYear=parseInt(currentDate.getUTCFullYear());
currentMonth=parseInt(currentDate.getUTCMonth())+1;
if (currentMonth<10) { currentMonth='0'+currentMonth; }

//
// Variables de entorno
//
var html=document.getElementsByTagName('html')[0].innerHTML;
var variables=html.split('<script type="text/javascript">')[1].split("</script>")[0];
var raw_vars=variables.substring(4,variables.length-2).split(",\n");
var vars=[];
for (var i=0;i<raw_vars.length;i++)
{
	var var_name=raw_vars[i].split("=", 1)[0];
	var var_value=raw_vars[i].split("=", 2)[1];
	var_value=var_value.substring(1,var_value.length-1);
	
	vars[var_name]=var_value;
}

//
// Chequeo de permisos de edición
//
var canEdit=false;
if (vars["wgRestrictionEdit"].length>0) {
   for (var i=0;i<vars["wgUserGroups"].length;i++) {
      if (vars["wgRestrictionEdit"][0]==vars["wgUserGroups"][i]) { canEdit=true; }
   }
}else{
   canEdit=true;
}

//
// AJAX
// 
var rcp_http_tablon;
var rcp_http_marquee;
var rcp_http_saltar;

rcp_init ();

function rcp_init() {
  rcp_ajax_request_tablon();
  rcp_ajax_request_marquee();
	rcp_ajax_request_saltar();


}
/* init ajax */
function rcp_create_request(rcp_ajax_response, rcp_http) {
   try {
      rcp_http = new XMLHttpRequest();
   } catch (e) {
      try {
         rcp_http = new ActiveXObject("Msxml2.XMLHTTP");
      } catch (e) {
         try {
            rcp_http = new ActiveXObject("Microsoft.XMLHTTP");
         } catch (e) {
            alert("Your browser does not support AJAX");
            return false;
         }
      }
   }
   rcp_http.onreadystatechange = function() {
      if(rcp_http.readyState == 4) rcp_ajax_response(rcp_http);
   }
   return rcp_http;
}

// AJAX para tablon
function rcp_ajax_request_tablon() {
   rcp_http_tablon=rcp_create_request (rcp_ajax_response_tablon, rcp_http_tablon);
   // Then make the request
   rcp_http_tablon.open("GET", vars["wgServer"] + vars["wgScriptPath"] + "/api.php?action=query&prop=revisions&titles=User:Emijrp/Zona de pruebas&rvprop=content&format=xml", true);
   rcp_http_tablon.send(null);
}
 
// Respuesta AJAX para tablon
function rcp_ajax_response_tablon(rcp_http) {
   var items = rcp_http.responseXML.getElementsByTagName('rev');
   var text = items[0].childNodes[0].nodeValue;

temp=text.split("\n");
text2="";
for (var i =0;i<temp.length;i++)
{
	temp2=temp[i].split(";;;");
	text2+=temp2[0]+" > "+temp2[1]+"\n";
}

document.getElementById('tablon').innerHTML=text2;
}
 
// AJAX para marquee
function rcp_ajax_request_marquee() {
   rcp_http_marquee=rcp_create_request (rcp_ajax_response_marquee, rcp_http_marquee);
   // Then make the request
   rcp_http_marquee.open("GET", vars["wgServer"] + vars["wgScriptPath"] + "/api.php?action=query&list=recentchanges&rctype=new&rcnamespace=0&rcshow=!redirect&rcprop=title|user|sizes&rclimit=5&format=xml", true);
   rcp_http_marquee.send(null);
}
 
// Respuesta AJAX para marquee
function rcp_ajax_response_marquee(rcp_http) {
   var items = rcp_http.responseXML.getElementsByTagName('rc');
   
var text="";
for (var i=0;i<items.length;i++)
{
	var title=items[i].getAttribute('title');
	var user=items[i].getAttribute('user');
	var pagelen=parseInt(items[i].getAttribute('newlen'));
	text+=" <a href=\""+vars["wgServer"]+"/wiki/"+title+"\">"+title+"</a> ["+pagelen+" bytes] ["+user+"]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
}

document.getElementById('marqueespan').innerHTML=text;
}

// AJAX para saltar a la inglesa
function rcp_ajax_request_saltar() {
   rcp_http_saltar=rcp_create_request (rcp_ajax_response_saltar, rcp_http_saltar);
   // Then make the request
   rcp_http_saltar.open("GET", vars["wgServer"] + vars["wgScriptPath"] + "/api.php?action=query&prop=langlinks&titles="+vars["wgPageName"]+"&lllimit=500&format=xml", true);
   rcp_http_saltar.send(null);
}
 
// Respuesta AJAX saltar a la inglesa
function rcp_ajax_response_saltar(rcp_http) {
   var items = rcp_http.responseXML.getElementsByTagName('ll');
var text="";
for (var i=0;i<items.length;i++)
{
	var lang=items[i].getAttribute("lang");
	var wtitle=items[i].childNodes[0].nodeValue;
	if (lang=="en")
	{
		document.getElementById("firstHeading").innerHTML+=" <span style=\"font-size: small;\"><i>(Saltar a la <a href=\"http://en.wikipedia.org/wiki/"+wtitle+"\">inglesa</a>)</i></span>";
		break;
	}
}

document.getElementById('saltar').innerHTML=text;
}
 



//logo
document.getElementById("p-logo").innerHTML="<br/><center><a href=\"http://es.wikipedia.org\"><img src=\"http://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Glider.svg/140px-Glider.svg.png\" /></a></center>";

//menú navegación
document.getElementById("p-navigation").innerHTML="<h5 lang=\"es\" xml:lang=\"es\">Navegación</h5>\n<div class='pBody'>\n<ul>\n<li id=\"n-mainpage-description\"><a href=\"/\" title=\"Visitar la página principal [z]\" accesskey=\"z\">Portada</a></li><li id=\"n-featured\"><a href=\"/wiki/Wikipedia:Artículos destacados\">Contenido destacado</a></li><li id=\"n-currentevents\"><a href=\"/wiki/Portal:Actualidad\" title=\"Información de contexto sobre acontecimientos actuales\">Actualidad</a></li><li id=\"n-recentchanges\"><a href=\"/wiki/Especial:CambiosRecientes\" title=\"La lista de cambios recientes en el wiki [r]\" accesskey=\"r\">Cambios recientes</a></li><li id=\"n-randompage\"><a href=\"/wiki/Especial:Aleatoria\" title=\"Cargar una página aleatoriamente [x]\" accesskey=\"x\">Aleatoria</a></li></ul>\n</div>";

//menú enlaces personales
//beta
document.getElementById("pt-optin-try").innerHTML="";
//botón de salir
document.getElementById("pt-logout").innerHTML="";
document.getElementById("pt-mycontris").innerHTML+=" (<a href=\"/w/api.php?action=query&list=users&ususers="+vars["wgUserName"]+"&usprop=editcount\">num</a>)";
document.getElementById("pt-mytalk").innerHTML+=" (<a href=\"/w/index.php?title=Usuario_Discusión:Emijrp&action=history\">hist</a>)";

//cosas para borrar
//enlace de donaciones
//enlace de subir archivo: no, que lleva a Commons

//Recentchanges
if (vars["wgCanonicalNamespace"]=="Special" && vars["wgCanonicalSpecialPageName"]=="Recentchanges")
{
	var new_element = document.createElement('li');
	new_element.innerHTML = "&nbsp;&nbsp;<a href=\"/wiki/Special:Contributions/newbies\">novatos</a>&nbsp;&nbsp;";
	var new_element2 = document.createElement('li');
	new_element2.innerHTML = "&nbsp;&nbsp;<a href=\"/wiki/Special:Newpages\">Páginas nuevas</a>&nbsp;&nbsp;";
	
	container=document.getElementById("p-cactions");
	container=container.getElementsByTagName("div")[0];
	container=container.getElementsByTagName("ul")[0];
	container.insertBefore(new_element, container.lastChild);
	container.insertBefore(new_element2, container.lastChild);

	document.body.innerHTML=document.body.innerHTML.split("<!-- start content -->")[0]+"<!-- start content --> <fieldset"+document.body.innerHTML.split("<fieldset")[1];
}

//Newpages
if (vars["wgCanonicalNamespace"]=="Special" && vars["wgCanonicalSpecialPageName"]=="Newpages")
{
	var new_element = document.createElement('li');
	new_element.innerHTML = "&nbsp;&nbsp;<a href=\"/wiki/Special:Contributions/newbies\">novatos</a>&nbsp;&nbsp;";
	var new_element2 = document.createElement('li');
	new_element2.innerHTML = "&nbsp;&nbsp;<a href=\"/wiki/Special:Recentchanges\">Cambios recientes</a>&nbsp;&nbsp;";
	
	container=document.getElementById("p-cactions");
	container=container.getElementsByTagName("div")[0];
	container=container.getElementsByTagName("ul")[0];
	container.insertBefore(new_element, container.lastChild);
	container.insertBefore(new_element2, container.lastChild);

	document.body.innerHTML=document.body.innerHTML.split("<!-- start content -->")[0]+"<!-- start content --> <fieldset"+document.body.innerHTML.split("<fieldset")[1];
}

//Página de usuario cualquiera
if (vars["wgCanonicalNamespace"]=="User")
{
	var new_element = document.createElement('li');
	new_element.innerHTML = "<a href=\"/wiki/Special:Contributions/"+vars["wgTitle"]+"\">Contribuciones</a>";
	var new_element2 = document.createElement('li');
	new_element2.innerHTML = "<a href=\"/w/index.php?title=Usuario_Discusión:"+vars["wgTitle"]+"&action=edit&section=new\">SMS</a>";
	
	container=document.getElementById("p-cactions");
	container=container.getElementsByTagName("div")[0];
	container=container.getElementsByTagName("ul")[0];
	container.insertBefore(new_element, container.lastChild);
	container.insertBefore(new_element2, container.lastChild);
}

//namespace!=-1
if (vars["wgNamespace"]!=-1)
{
	var new_element = document.createElement('li');
	new_element.innerHTML = "<a href=\"/w/index.php?title=Especial:LoQueEnlazaAquí/"+vars["wgTitle"]+"&hidelinks=1&hidetrans=1\">Redirecciones</a>";

	container=document.getElementById("p-cactions");
	container=container.getElementsByTagName("div")[0];
	container=container.getElementsByTagName("ul")[0];
	container.insertBefore(new_element, container.lastChild);
}

//cualquier namespace
container=document.getElementById("p-cactions");
container=container.getElementsByTagName("div")[0];
container=container.getElementsByTagName("ul")[0];

var new_element = document.createElement('li');
var new_element2 = document.createElement('li');
new_element.innerHTML = "<a onclick=\"javascript:var container=document.getElementById('iframevisitas');if (container.style.display=='none') { container.style.display='';  }else{ container.style.display='none'; }\">Visitas</a>";
container.insertBefore(new_element, container.lastChild);
new_element2.innerHTML = "<a onclick=\"javascript:var container=document.getElementById('iframeautores');if (container.style.display=='none') { container.style.display='';  }else{ container.style.display='none'; }\">Autores</a>";
container.insertBefore(new_element2, container.lastChild);

//inicio tablón

var board = document.createElement('div');
board.className="generated-sidebar portlet";
board.id="p-board";
board.innerHTML="<h5 lang=\"es\" xml:lang=\"es\">Tablón</h5>";
board.innerHTML+="<div class='pBody'>";
board.innerHTML+="<textarea id=\"tablon\" rows=7 cols=5 readonly>";
board.innerHTML+="</textarea>";
board.innerHTML+="<input id=\"tabloncajetin\" type=\"text\" size=10 value=\"saluda...\" onclick=\"javascript:if (document.getElementById('tabloncajetin').value=='saluda...') document.getElementById('tabloncajetin').value=''\"><input type=\"submit\" value=\"↲\">";
board.innerHTML+="</div>";
board.innerHTML+="</div>";
container=document.getElementById("column-one");
container.insertBefore(board, document.getElementById("p-coll-print_export"));

//fin tablón

//inicio marquesina
var marquee=document.createElement('div');
var descanso="";
for (var i=0;i<250;i++)
	descanso+="&nbsp;";
//capturar paginas nuevas

marquee.innerHTML="<center><MARQUEE bgcolor = \"#FFFFFF\" width = 75% scrolldelay = 100 loop = infinite ><b>Nuevos</b>&nbsp;&nbsp;&nbsp;<span id='marqueespan'></span>"+descanso+"</MARQUEE></center>";
content=document.getElementById('content');
content.insertBefore(marquee, content.firstChild);
//fin marquesina

//ocultar buscador
//document.getElementById("p-search").style.display="none";

//document.getElementById("siteSub").style.display="block";


document.getElementById("contentSub").innerHTML+="<center><iframe style=\"display:none;\" id=\"iframevisitas\"  frameborder=0  vspace=0  hspace=0  marginwidth=0  marginheight=0 width=1000  scrolling=yes  height=600  src=\"http://stats.grok.se/"+vars["wgContentLanguage"]+"/"+currentYear+currentMonth+"/"+vars["wgPageName"]+"\"></iframe></center>";
document.getElementById("contentSub").innerHTML+="<center><iframe style=\"display:none;\" id=\"iframeautores\"  frameborder=0  vspace=0  hspace=0  marginwidth=0  marginheight=0 width=1000  scrolling=yes  height=600  src=\"http://toolserver.org/~daniel/WikiSense/Contributors.php?wikilang="+vars["wgContentLanguage"]+"&wikifam=.wikipedia.org&page="+vars["wgTitle"]+"&grouped=on&order=-edit_count&max=200&format=html\"></iframe></center>";

//alert(wgUserName);
//alert(a);
// Create a new <li> element for to insert inside <ul id="myList">
/*var new_element = document.createElement('li');
new_element.innerHTML = element;
container.insertBefore(new_element, container.firstChild);
*/

