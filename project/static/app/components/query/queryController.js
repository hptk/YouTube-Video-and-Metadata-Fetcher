'use strict';

define(['app'], function (app) {

    
    app.register.controller('queryController', ['APIKeyService','queryService','taskService', '$rootScope','$routeParams','$location','$timeout',
     function (APIKeyService,queryService,taskService, $rootScope, $routeParams, $location, $timeout) {

        var vm = this;
        vm.optionalIsCollapsed = true;
        vm.channelType = [
                          { name: 'Return all channels' , type:'any'},
                          { name: 'Only retrieve shows' , type:'show'}
                          ];
        vm.eventType = [
                          { name: 'Only include completed broadcasts' , type:'completed'},
                          { name: 'Only include active boradcasts' , type:'live'},
                          { name: 'Only include upcoming broadcasts' , type:'upcoming'}
                          
                          ];
        vm.regionCode = [{"name":"Afghanistan","code":"AF"},{"name":"Åland Islands","code":"AX"},{"name":"Albania","code":"AL"},{"name":"Algeria","code":"DZ"},{"name":"American Samoa","code":"AS"},{"name":"Andorra","code":"AD"},{"name":"Angola","code":"AO"},{"name":"Anguilla","code":"AI"},{"name":"Antarctica","code":"AQ"},{"name":"Antigua and Barbuda","code":"AG"},{"name":"Argentina","code":"AR"},{"name":"Armenia","code":"AM"},{"name":"Aruba","code":"AW"},{"name":"Australia","code":"AU"},{"name":"Austria","code":"AT"},{"name":"Azerbaijan","code":"AZ"},{"name":"Bahamas","code":"BS"},{"name":"Bahrain","code":"BH"},{"name":"Bangladesh","code":"BD"},{"name":"Barbados","code":"BB"},{"name":"Belarus","code":"BY"},{"name":"Belgium","code":"BE"},{"name":"Belize","code":"BZ"},{"name":"Benin","code":"BJ"},{"name":"Bermuda","code":"BM"},{"name":"Bhutan","code":"BT"},{"name":"Bolivia, Plurinational State of","code":"BO"},{"name":"Bonaire, Sint Eustatius and Saba","code":"BQ"},{"name":"Bosnia and Herzegovina","code":"BA"},{"name":"Botswana","code":"BW"},{"name":"Bouvet Island","code":"BV"},{"name":"Brazil","code":"BR"},{"name":"British Indian Ocean Territory","code":"IO"},{"name":"Brunei Darussalam","code":"BN"},{"name":"Bulgaria","code":"BG"},{"name":"Burkina Faso","code":"BF"},{"name":"Burundi","code":"BI"},{"name":"Cambodia","code":"KH"},{"name":"Cameroon","code":"CM"},{"name":"Canada","code":"CA"},{"name":"Cape Verde","code":"CV"},{"name":"Cayman Islands","code":"KY"},{"name":"Central African Republic","code":"CF"},{"name":"Chad","code":"TD"},{"name":"Chile","code":"CL"},{"name":"China","code":"CN"},{"name":"Christmas Island","code":"CX"},{"name":"Cocos (Keeling) Islands","code":"CC"},{"name":"Colombia","code":"CO"},{"name":"Comoros","code":"KM"},{"name":"Congo","code":"CG"},{"name":"Congo, the Democratic Republic of the","code":"CD"},{"name":"Cook Islands","code":"CK"},{"name":"Costa Rica","code":"CR"},{"name":"Côte d'Ivoire","code":"CI"},{"name":"Croatia","code":"HR"},{"name":"Cuba","code":"CU"},{"name":"Curaçao","code":"CW"},{"name":"Cyprus","code":"CY"},{"name":"Czech Republic","code":"CZ"},{"name":"Denmark","code":"DK"},{"name":"Djibouti","code":"DJ"},{"name":"Dominica","code":"DM"},{"name":"Dominican Republic","code":"DO"},{"name":"Ecuador","code":"EC"},{"name":"Egypt","code":"EG"},{"name":"El Salvador","code":"SV"},{"name":"Equatorial Guinea","code":"GQ"},{"name":"Eritrea","code":"ER"},{"name":"Estonia","code":"EE"},{"name":"Ethiopia","code":"ET"},{"name":"Falkland Islands (Malvinas)","code":"FK"},{"name":"Faroe Islands","code":"FO"},{"name":"Fiji","code":"FJ"},{"name":"Finland","code":"FI"},{"name":"France","code":"FR"},{"name":"French Guiana","code":"GF"},{"name":"French Polynesia","code":"PF"},{"name":"French Southern Territories","code":"TF"},{"name":"Gabon","code":"GA"},{"name":"Gambia","code":"GM"},{"name":"Georgia","code":"GE"},{"name":"Germany","code":"DE"},{"name":"Ghana","code":"GH"},{"name":"Gibraltar","code":"GI"},{"name":"Greece","code":"GR"},{"name":"Greenland","code":"GL"},{"name":"Grenada","code":"GD"},{"name":"Guadeloupe","code":"GP"},{"name":"Guam","code":"GU"},{"name":"Guatemala","code":"GT"},{"name":"Guernsey","code":"GG"},{"name":"Guinea","code":"GN"},{"name":"Guinea-Bissau","code":"GW"},{"name":"Guyana","code":"GY"},{"name":"Haiti","code":"HT"},{"name":"Heard Island and McDonald Islands","code":"HM"},{"name":"Holy See (Vatican City State)","code":"VA"},{"name":"Honduras","code":"HN"},{"name":"Hong Kong","code":"HK"},{"name":"Hungary","code":"HU"},{"name":"Iceland","code":"IS"},{"name":"India","code":"IN"},{"name":"Indonesia","code":"ID"},{"name":"Iran, Islamic Republic of","code":"IR"},{"name":"Iraq","code":"IQ"},{"name":"Ireland","code":"IE"},{"name":"Isle of Man","code":"IM"},{"name":"Israel","code":"IL"},{"name":"Italy","code":"IT"},{"name":"Jamaica","code":"JM"},{"name":"Japan","code":"JP"},{"name":"Jersey","code":"JE"},{"name":"Jordan","code":"JO"},{"name":"Kazakhstan","code":"KZ"},{"name":"Kenya","code":"KE"},{"name":"Kiribati","code":"KI"},{"name":"Korea, Democratic People's Republic of","code":"KP"},{"name":"Korea, Republic of","code":"KR"},{"name":"Kuwait","code":"KW"},{"name":"Kyrgyzstan","code":"KG"},{"name":"Lao People's Democratic Republic","code":"LA"},{"name":"Latvia","code":"LV"},{"name":"Lebanon","code":"LB"},{"name":"Lesotho","code":"LS"},{"name":"Liberia","code":"LR"},{"name":"Libya","code":"LY"},{"name":"Liechtenstein","code":"LI"},{"name":"Lithuania","code":"LT"},{"name":"Luxembourg","code":"LU"},{"name":"Macao","code":"MO"},{"name":"Macedonia, the Former Yugoslav Republic of","code":"MK"},{"name":"Madagascar","code":"MG"},{"name":"Malawi","code":"MW"},{"name":"Malaysia","code":"MY"},{"name":"Maldives","code":"MV"},{"name":"Mali","code":"ML"},{"name":"Malta","code":"MT"},{"name":"Marshall Islands","code":"MH"},{"name":"Martinique","code":"MQ"},{"name":"Mauritania","code":"MR"},{"name":"Mauritius","code":"MU"},{"name":"Mayotte","code":"YT"},{"name":"Mexico","code":"MX"},{"name":"Micronesia, Federated States of","code":"FM"},{"name":"Moldova, Republic of","code":"MD"},{"name":"Monaco","code":"MC"},{"name":"Mongolia","code":"MN"},{"name":"Montenegro","code":"ME"},{"name":"Montserrat","code":"MS"},{"name":"Morocco","code":"MA"},{"name":"Mozambique","code":"MZ"},{"name":"Myanmar","code":"MM"},{"name":"Namibia","code":"NA"},{"name":"Nauru","code":"NR"},{"name":"Nepal","code":"NP"},{"name":"Netherlands","code":"NL"},{"name":"New Caledonia","code":"NC"},{"name":"New Zealand","code":"NZ"},{"name":"Nicaragua","code":"NI"},{"name":"Niger","code":"NE"},{"name":"Nigeria","code":"NG"},{"name":"Niue","code":"NU"},{"name":"Norfolk Island","code":"NF"},{"name":"Northern Mariana Islands","code":"MP"},{"name":"Norway","code":"NO"},{"name":"Oman","code":"OM"},{"name":"Pakistan","code":"PK"},{"name":"Palau","code":"PW"},{"name":"Palestine, State of","code":"PS"},{"name":"Panama","code":"PA"},{"name":"Papua New Guinea","code":"PG"},{"name":"Paraguay","code":"PY"},{"name":"Peru","code":"PE"},{"name":"Philippines","code":"PH"},{"name":"Pitcairn","code":"PN"},{"name":"Poland","code":"PL"},{"name":"Portugal","code":"PT"},{"name":"Puerto Rico","code":"PR"},{"name":"Qatar","code":"QA"},{"name":"Réunion","code":"RE"},{"name":"Romania","code":"RO"},{"name":"Russian Federation","code":"RU"},{"name":"Rwanda","code":"RW"},{"name":"Saint Barthélemy","code":"BL"},{"name":"Saint Helena, Ascension and Tristan da Cunha","code":"SH"},{"name":"Saint Kitts and Nevis","code":"KN"},{"name":"Saint Lucia","code":"LC"},{"name":"Saint Martin (French part)","code":"MF"},{"name":"Saint Pierre and Miquelon","code":"PM"},{"name":"Saint Vincent and the Grenadines","code":"VC"},{"name":"Samoa","code":"WS"},{"name":"San Marino","code":"SM"},{"name":"Sao Tome and Principe","code":"ST"},{"name":"Saudi Arabia","code":"SA"},{"name":"Senegal","code":"SN"},{"name":"Serbia","code":"RS"},{"name":"Seychelles","code":"SC"},{"name":"Sierra Leone","code":"SL"},{"name":"Singapore","code":"SG"},{"name":"Sint Maarten (Dutch part)","code":"SX"},{"name":"Slovakia","code":"SK"},{"name":"Slovenia","code":"SI"},{"name":"Solomon Islands","code":"SB"},{"name":"Somalia","code":"SO"},{"name":"South Africa","code":"ZA"},{"name":"South Georgia and the South Sandwich Islands","code":"GS"},{"name":"South Sudan","code":"SS"},{"name":"Spain","code":"ES"},{"name":"Sri Lanka","code":"LK"},{"name":"Sudan","code":"SD"},{"name":"Suriname","code":"SR"},{"name":"Svalbard and Jan Mayen","code":"SJ"},{"name":"Swaziland","code":"SZ"},{"name":"Sweden","code":"SE"},{"name":"Switzerland","code":"CH"},{"name":"Syrian Arab Republic","code":"SY"},{"name":"Taiwan, Province of China","code":"TW"},{"name":"Tajikistan","code":"TJ"},{"name":"Tanzania, United Republic of","code":"TZ"},{"name":"Thailand","code":"TH"},{"name":"Timor-Leste","code":"TL"},{"name":"Togo","code":"TG"},{"name":"Tokelau","code":"TK"},{"name":"Tonga","code":"TO"},{"name":"Trinidad and Tobago","code":"TT"},{"name":"Tunisia","code":"TN"},{"name":"Turkey","code":"TR"},{"name":"Turkmenistan","code":"TM"},{"name":"Turks and Caicos Islands","code":"TC"},{"name":"Tuvalu","code":"TV"},{"name":"Uganda","code":"UG"},{"name":"Ukraine","code":"UA"},{"name":"United Arab Emirates","code":"AE"},{"name":"United Kingdom","code":"GB"},{"name":"United States","code":"US"},{"name":"United States Minor Outlying Islands","code":"UM"},{"name":"Uruguay","code":"UY"},{"name":"Uzbekistan","code":"UZ"},{"name":"Vanuatu","code":"VU"},{"name":"Venezuela, Bolivarian Republic of","code":"VE"},{"name":"Viet Nam","code":"VN"},{"name":"Virgin Islands, British","code":"VG"},{"name":"Virgin Islands, U.S.","code":"VI"},{"name":"Wallis and Futuna","code":"WF"},{"name":"Western Sahara","code":"EH"},{"name":"Yemen","code":"YE"},{"name":"Zambia","code":"ZM"},{"name":"Zimbabwe","code":"ZW"}];
        
        vm.relevanceLanguage = [{"code":"aa","name":"Afar"},{"code":"ab","name":"Abkhazian"},{"code":"ae","name":"Avestan"},{"code":"af","name":"Afrikaans"},{"code":"ak","name":"Akan"},{"code":"am","name":"Amharic"},{"code":"an","name":"Aragonese"},{"code":"ar","name":"Arabic"},{"code":"as","name":"Assamese"},{"code":"av","name":"Avaric"},{"code":"ay","name":"Aymara"},{"code":"az","name":"Azerbaijani"},{"code":"ba","name":"Bashkir"},{"code":"be","name":"Belarusian"},{"code":"bg","name":"Bulgarian"},{"code":"bh","name":"Bihari languages"},{"code":"bi","name":"Bislama"},{"code":"bm","name":"Bambara"},{"code":"bn","name":"Bengali"},{"code":"bo","name":"Tibetan"},{"code":"br","name":"Breton"},{"code":"bs","name":"Bosnian"},{"code":"ca","name":"Catalan; Valencian"},{"code":"ce","name":"Chechen"},{"code":"ch","name":"Chamorro"},{"code":"co","name":"Corsican"},{"code":"cr","name":"Cree"},{"code":"cs","name":"Czech"},{"code":"cu","name":"Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic"},{"code":"cv","name":"Chuvash"},{"code":"cy","name":"Welsh"},{"code":"da","name":"Danish"},{"code":"de","name":"German"},{"code":"dv","name":"Divehi; Dhivehi; Maldivian"},{"code":"dz","name":"Dzongkha"},{"code":"ee","name":"Ewe"},{"code":"el","name":"Greek, Modern (1453-)"},{"code":"en","name":"name"},{"code":"eo","name":"Esperanto"},{"code":"es","name":"Spanish; Castilian"},{"code":"et","name":"Estonian"},{"code":"eu","name":"Basque"},{"code":"fa","name":"Persian"},{"code":"ff","name":"Fulah"},{"code":"fi","name":"Finnish"},{"code":"fj","name":"Fijian"},{"code":"fo","name":"Faroese"},{"code":"fr","name":"French"},{"code":"fy","name":"Western Frisian"},{"code":"ga","name":"Irish"},{"code":"gd","name":"Gaelic; Scottish Gaelic"},{"code":"gl","name":"Galician"},{"code":"gn","name":"Guarani"},{"code":"gu","name":"Gujarati"},{"code":"gv","name":"Manx"},{"code":"ha","name":"Hausa"},{"code":"he","name":"Hebrew"},{"code":"hi","name":"Hindi"},{"code":"ho","name":"Hiri Motu"},{"code":"hr","name":"Croatian"},{"code":"ht","name":"Haitian; Haitian Creole"},{"code":"hu","name":"Hungarian"},{"code":"hy","name":"Armenian"},{"code":"hz","name":"Herero"},{"code":"ia","name":"Interlingua (International Auxiliary Language Association)"},{"code":"id","name":"Indonesian"},{"code":"ie","name":"Interlingue; Occidental"},{"code":"ig","name":"Igbo"},{"code":"ii","name":"Sichuan Yi; Nuosu"},{"code":"ik","name":"Inupiaq"},{"code":"io","name":"Ido"},{"code":"is","name":"Icelandic"},{"code":"it","name":"Italian"},{"code":"iu","name":"Inuktitut"},{"code":"ja","name":"Japanese"},{"code":"jv","name":"Javanese"},{"code":"ka","name":"Georgian"},{"code":"kg","name":"Kongo"},{"code":"ki","name":"Kikuyu; Gikuyu"},{"code":"kj","name":"Kuanyama; Kwanyama"},{"code":"kk","name":"Kazakh"},{"code":"kl","name":"Kalaallisut; Greenlandic"},{"code":"km","name":"Central Khmer"},{"code":"kn","name":"Kannada"},{"code":"ko","name":"Korean"},{"code":"kr","name":"Kanuri"},{"code":"ks","name":"Kashmiri"},{"code":"ku","name":"Kurdish"},{"code":"kv","name":"Komi"},{"code":"kw","name":"Cornish"},{"code":"ky","name":"Kirghiz; Kyrgyz"},{"code":"la","name":"Latin"},{"code":"lb","name":"Luxembourgish; Letzeburgesch"},{"code":"lg","name":"Ganda"},{"code":"li","name":"Limburgan; Limburger; Limburgish"},{"code":"ln","name":"Lingala"},{"code":"lo","name":"Lao"},{"code":"lt","name":"Lithuanian"},{"code":"lu","name":"Luba-Katanga"},{"code":"lv","name":"Latvian"},{"code":"mg","name":"Malagasy"},{"code":"mh","name":"Marshallese"},{"code":"mi","name":"Maori"},{"code":"mk","name":"Macedonian"},{"code":"ml","name":"Malayalam"},{"code":"mn","name":"Mongolian"},{"code":"mr","name":"Marathi"},{"code":"ms","name":"Malay"},{"code":"mt","name":"Maltese"},{"code":"my","name":"Burmese"},{"code":"na","name":"Nauru"},{"code":"nb","name":"Bokmål, Norwegian; Norwegian Bokmål"},{"code":"nd","name":"Ndebele, North; North Ndebele"},{"code":"ne","name":"Nepali"},{"code":"ng","name":"Ndonga"},{"code":"nl","name":"Dutch; Flemish"},{"code":"nn","name":"Norwegian Nynorsk; Nynorsk, Norwegian"},{"code":"no","name":"Norwegian"},{"code":"nr","name":"Ndebele, South; South Ndebele"},{"code":"nv","name":"Navajo; Navaho"},{"code":"ny","name":"Chichewa; Chewa; Nyanja"},{"code":"oc","name":"Occitan (post 1500); Provençal"},{"code":"oj","name":"Ojibwa"},{"code":"om","name":"Oromo"},{"code":"or","name":"Oriya"},{"code":"os","name":"Ossetian; Ossetic"},{"code":"pa","name":"Panjabi; Punjabi"},{"code":"pi","name":"Pali"},{"code":"pl","name":"Polish"},{"code":"ps","name":"Pushto; Pashto"},{"code":"pt","name":"Portuguese"},{"code":"qu","name":"Quechua"},{"code":"rm","name":"Romansh"},{"code":"rn","name":"Rundi"},{"code":"ro","name":"Romanian; Moldavian; Moldovan"},{"code":"ru","name":"Russian"},{"code":"rw","name":"Kinyarwanda"},{"code":"sa","name":"Sanskrit"},{"code":"sc","name":"Sardinian"},{"code":"sd","name":"Sindhi"},{"code":"se","name":"Northern Sami"},{"code":"sg","name":"Sango"},{"code":"si","name":"Sinhala; Sinhalese"},{"code":"sk","name":"Slovak"},{"code":"sl","name":"Slovenian"},{"code":"sm","name":"Samoan"},{"code":"sn","name":"Shona"},{"code":"so","name":"Somali"},{"code":"sq","name":"Albanian"},{"code":"sr","name":"Serbian"},{"code":"ss","name":"Swati"},{"code":"st","name":"Sotho, Southern"},{"code":"su","name":"Sundanese"},{"code":"sv","name":"Swedish"},{"code":"sw","name":"Swahili"},{"code":"ta","name":"Tamil"},{"code":"te","name":"Telugu"},{"code":"tg","name":"Tajik"},{"code":"th","name":"Thai"},{"code":"ti","name":"Tigrinya"},{"code":"tk","name":"Turkmen"},{"code":"tl","name":"Tagalog"},{"code":"tn","name":"Tswana"},{"code":"to","name":"Tonga (Tonga Islands)"},{"code":"tr","name":"Turkish"},{"code":"ts","name":"Tsonga"},{"code":"tt","name":"Tatar"},{"code":"tw","name":"Twi"},{"code":"ty","name":"Tahitian"},{"code":"ug","name":"Uighur; Uyghur"},{"code":"uk","name":"Ukrainian"},{"code":"ur","name":"Urdu"},{"code":"uz","name":"Uzbek"},{"code":"ve","name":"Venda"},{"code":"vi","name":"Vietnamese"},{"code":"vo","name":"Volapük"},{"code":"wa","name":"Walloon"},{"code":"wo","name":"Wolof"},{"code":"xh","name":"Xhosa"},{"code":"yi","name":"Yiddish"},{"code":"yo","name":"Yoruba"},{"code":"za","name":"Zhuang; Chuang"},{"code":"zh","name":"Chinese"},{"code":"zu","name":"Zulu"}];
        
        vm.safeSearch = [
							{ name: 'YouTube will not filter the search result set.' , type:'none'},
							{ name: 'YouTube will filter some content from search results and, at the least, will filter content that is restricted in your locale. Based on their content, search results could be removed from search results or demoted in search results. This is the default parameter value.' , type:'moderate'},
							{ name: 'YouTube will try to exclude all restricted content from the search result set. Based on their content, search results could be removed from search results or demoted in search results.' , type:'strict'}
                         ];
        
        vm.videoCaption = [
                           { type:"any", name:"Do not filter results based on caption availability"},
                           { type:"closedCaption", name:"Only include videos that have captions"},
                           { type:"none", name:"Only include videos that do not have captions"}
                           ];
        
        vm.videoDefinition = [
                           { type:"any", name:"Return all videos, regardless of their resolution"},
                           { type:"high", name:"Only retrieve HD videos"},
                           { type:"standard", name:"Only retrieve videos in standard definition"}
                           ];
        
        vm.videoDimension = [
                              { type:"any", name:"Include both, 3D and non-3D videos in returned results. This is the default value"},
                              { type:"2d", name:"Restrict search results to exclude 3D videos"},
                              { type:"3d", name:"Restrict search results to exclude 2D videos"}
                              ];
        
        vm.videoDuration = [
                              { type:"any", name:"Do not filter video search results based on their duration. This is the default value"},
                              { type:"short", name:"Only include videos that are less than 4 minutes long"},
                              { type:"medium", name:"Only include videos that are between 4 and 20 minutes long (inclusive)"},
                              { type:"long", name:"Only include videos longer than 20 minutes"}
                              ];
        
        /*
         * default query parameter
         * */
        vm.query = {
        	type:"video",
        };
       
    	
        vm.loadOldQueries = loadOldQueries;
        vm.createQuery = createQuery;
        vm.changeToQuery = changeToQuery;
        vm.createTask = createTask;
        vm.changeToTasks = changeToTasks;
        vm.changeToResults = changeToResults;
        
        var today = new Date();
        vm.datepicker = {
        		format:"dd.MM.yyyy",
        		publishedAfter: {
        			maxDate:today
        		},
        		publishedBefore: {
        			maxDate:today
        		}
        		
        };
        
        vm.APIKeyList = [];
        vm.oldQueries = [];
        vm.maxOldQueries = {
        	    availableOptions: [
        	      {value: '10', name: '10'},
        	      {value: '20', name: '20'},
        	      {value: '30', name: '30'},
        	      {value: '40', name: '40'},
        	      {value: '50', name: '50'},
        	      {value: '100', name: '100'}
        	    ],
        	    selectedOption: {value: '20', name: '20'} //This sets the default value of the select in the ui
        	    };
        initController();
        
        
        function initController() {
        	
            loadAllKeys();
            loadOldQueries();
            if(typeof $routeParams.id !== 'undefined') {
            	loadHashQuery();
            }
        }
        
        function changeToQuery(id) {
        	$location.path("/query/"+id)
        }
        function changeToTasks() {
        	$location.path("/task/"+$routeParams.id)
        }
        function changeToResults() {
        	$location.path("/result/"+$routeParams.id)
        }
       function createTask(action) {
    	   vm.createTaskClicked = true;
    	   vm.dataCheckingQuery = true;
    	   
    	   taskService.createTask($routeParams.id,action)
   			.then(function (data) {
   				if(data.success===true)
   				{
   					vm.task = data.task;
   					vm.dataCheckingQuery = false;
   					updateProgress(vm.task.progress_url)
   				}
   				else
   				{
   					alert("some serverside error");
   					vm.createTaskClicked = false;
   					vm.dataCheckingQuery = false;
   				}
   			});
       }
       
       function updateProgress(url)
       {
    	   vm.showProgress=true;
    	   taskService.getProgress(url)
    	   .then(function (data) {
  				if(data.success!==false)
  				{
  					if(data.state=='PENDING') {
  						
  					} else {
  						vm.task.progress = angular.toJson(data);
  	  					vm.taskprogressmax = data.workQueueDone+data.workQueue;
  	  					vm.taskprogressvalue = data.workQueueDone;
  	  					vm.taskprogresscurrent = data.current;
  					}
  						
  					
  					if (data.state != 'PENDING' && data.state != 'PROGRESS' && data.state!='SAVING') {
  		                if ('result' in data) {
  		                    // show result
  		                	vm.task.result = data.result;
  		                	vm.taskprogresscurrent = data.result
  		                }
  		                else {
  		                    // something unexpected happened
  		                	vm.task.error = data.state;
  		                }
  		            }
  		            else {
  		                // rerun in 1 seconds
  		                $timeout(function(){updateProgress(url)},1000);
  		            }
  					vm.task.progress = angular.toJson(data);
  					
  				}
  				
  			});
    	   vm.dataCheckingQuery = false;
       }
       
       
        function loadAllKeys() {
        	APIKeyService.getAll()
        		.then(function (data) {
        			if(data.success===true)
        			{
        				vm.APIKeyList = data.keys;
        				angular.forEach(vm.APIKeyList,function(apikey) {
        					checkAvailability(apikey);
        				});
        			}
        	});
        }
        
        function loadHashQuery() {
        	queryService.getQuery($routeParams.id)
        		.then(function (data) {
        			if(data.success===true)
        			{
        				vm.loadedQuery = true
        				vm.dataCheckingQuery = true
        				vm.query = data.query.queryRaw;
        				vm.selectedOldQuery = data.query
        				queryService.testQuery(vm.query)
        	    		.then(function (response) {
        	    			if(response.code)
        	    			{
        	    				alert(response.message)
        	        			vm.dataCheckingQuery = false;
        	    			}
        	    			else {
        	    				vm.loadedQueryStatus = true
        	    				vm.dataCheckingQuery = false;
        	    	    	}
        	    	    			
        	    	    	});
        				vm.dataCheckingQuery = false;
        			} else {
        				vm.loadedQuery = false
        				alert("could not fetch query from server");
        			}
        		});
        }
     
        
        function loadOldQueries() {
        	
        	queryService.getAll(vm.maxOldQueries.selectedOption.value)
    		.then(function (data) {
    			if(data.success===true)
    			{
    				vm.oldQueries = data.queries;
    			}
    	});
        }
        
        function createQuery() {
            vm.dataLoading = true;
            
            //change publishedAfter to first second of the day
            vm.query.publishedAfter.setHours(0);
            vm.query.publishedAfter.setSeconds(1);
            
            //change publishedBefore to the end of the day
            vm.query.publishedBefore.setHours(23);
            vm.query.publishedBefore.setMinutes(59);
            vm.query.publishedBefore.setSeconds(59);
            
        	//modify timezones to exclude them from the requests
            var publishedAfter = vm.query.publishedAfter.setMinutes(vm.query.publishedAfter.getMinutes() - vm.query.publishedAfter.getTimezoneOffset());
            vm.query.publishedAfter = new Date(publishedAfter);
            
            var publishedBefore = vm.query.publishedBefore.setMinutes(vm.query.publishedBefore.getMinutes() - vm.query.publishedBefore.getTimezoneOffset());
            vm.query.publishedBefore = new Date(publishedBefore)
            
            
            queryService.testQuery(vm.query)
    		.then(function (response) {
    			if(response.code)
    			{
    				//some error
        			//vm.loadOldQueries();
    				//$location.path("/query/"+response.queryHash)
    				alert(response.message)
        			vm.dataLoading = false;
    			}
    			else {
    				queryService.create(vm.query)
    	    		.then(function (response) {
    	    			if(response.success===true)
    	    			{
    	        			//vm.loadOldQueries();
    	    				$location.path("/query/"+response.id)
    	        			vm.dataLoading = false;
    	    			}
    	    			else {
    	    				vm.dataLoading = false;
    	    			}
    	    		});
    				vm.dataLoading = false;
    			}
    		});
            
            
            
        }
        
        function checkAvailability(apikey) {
        	APIKeyService.checkAvailability(apikey.key)
        		.then(function (status) {
        			if(status)
        			{
        				apikey.availability=true;
        			}
        			else {
        				apikey.availability=false;
        			}
        	});
        }


     }]);
});