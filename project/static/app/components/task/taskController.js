'use strict';

define(['app'], function (app) {

    
    app.register.controller('taskController', ['APIKeyService','queryService','taskService', '$rootScope','$routeParams','$location','$timeout','$filter',
     function (APIKeyService,queryService,taskService, $rootScope, $routeParams, $location, $timeout,$filter) {

        var vm = this;

        vm.task = {
        		'actionOptions': {
        			'HTTPClients':50,
        			'ClientConnectionPool':50
        		}
        } 
        vm.loadOldQueries = loadOldQueries;
        vm.createTask = createTask;
        vm.oldTasks = [];
        vm.oldQueries = [];
        vm.runningTasks = [];
        vm.maxOldQueries = {
        	    availableOptions: [
        	      {value: '10', name: '10'},
        	      {value: '20', name: '20'},
        	      {value: '30', name: '30'},
        	      {value: '40', name: '40'},
        	      {value: '50', name: '50'},
        	      {value: '100', name: '100'}
        	    ],
        	    selectedOption: {value: '100', name: '100'} //This sets the default value of the select in the ui
        	    };
        
        vm.downloadResolutions = [{type:240 , name:"240p"},
                                  {type:360 , name:"360p"},
                                  {type:480 , name:"480p"},
                                  {type:720 , name:"720p"},
                                  {type:1080 , name:"1080p"},
                                  {type:1440 , name:"1440p"},
                                  {type:2160 , name:"2160p"}];
        
        vm.downloadSound = [{type:true , name:"With sound"},
                                  {type:false , name:"Without sound"}];
        
        vm.downloadMethod = [{type:'all' , name:"All"},
                             {type:'random' , name:"Random"}];
        
        vm.commentReplies = [{type:true , name:"With replies"},
                            {type:false , name:"Without replies"}];
  
        
        vm.taskOptions = [
							{ name: 'Fetches only the Video IDs for the selected query' , type:'IDFetcher'},
							{ name: 'Fetches the meta data for the videos which are associated with the selected query' , type:'MetaFetcher'},
							{ name: 'Fetches the the comments for the videos which are associated with the selected query' , type:'CommentFetcher'},
							{ name: 'Fetches the video informations from the DASH manifest to the database' , type:'ManifestFetcher'},
							{ name: 'Download the videos which are associated with the selected query' , type:'VideoFetcher'}
                      ];
        
        
        initController();
        
        
        function initController() {
        	
            loadOldQueries();
            if(typeof $routeParams.id !== 'undefined') {
            	loadHashQuery();
            }
        }
        
        function changeToQuery(id) {
        	$location.path("/query/"+id)
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
        
       function createTask(id,action) {
    	   vm.createTaskClicked = true;
    	   vm.dataCheckingQuery = true;
    	   taskService.createTask(id,action,vm.task.actionOptions)
   			.then(function (data) {
   				if(data.success===true)
   				{
   					//vm.task = data.task;
   					var taskCopy = angular.copy(data.task)
   					vm.dataCheckingQuery = false;
   					addTaskToList(taskCopy);
   					updateProgress(taskCopy)
   				}
   				else
   				{
   					alert("some serverside error");
   					vm.createTaskClicked = false;
   					vm.dataCheckingQuery = false;
   				}
   			});
       }
       function addTaskToList(task)
       {
    	   vm.runningTasks.push(task)
       }
       function removeTaskFromList(task)
       {
    	   
       }
       function getTaskFromList(task_id)
       {
    	   return $filter("filter")(vm.runningTasks,{task_id:task_id});
       }
       function updateProgress(task)
       {
    	   
    	   vm.showProgress=true;
    	   taskService.getProgress(task.progress_url)
    	   .then(function (data) {
  				if(data.success!==false)
  				{
  					if(data.state=='PENDING') {
  						
  					} else {
  						
  						task.progress = []
  						task.progress = data
  						task.progress.max = data.workQueueDone+data.workQueue;
  	  					//vm.taskprogressmax = data.workQueueDone+data.workQueue;
  	  					//vm.taskprogressvalue = data.workQueueDone;
  	  					//vm.taskprogresscurrent = data.current;
  					}
  						
  					
  					if (data.state != 'PENDING' && data.state != 'PROGRESS' && data.state!='SAVING' && data.state!='DONE') {
  		                if ('result' in data) {
  		                    // show result
  		                	task.result = data.result;
  		                	task.current = data.current;
  		                	//vm.taskprogresscurrent = data.result
  		                	vm.loadOldQueries()
  		                }
  		                else {
  		                    // something unexpected happened
  		                	task.error = data.state;
  		                }
  		            }
  		            else {
  		                // rerun in 1 seconds
  		                $timeout(function(){updateProgress(task)},1000);
  		            }
  					//vm.task.progress = angular.toJson(data);
  					
  				}
  				
  			});
    	   vm.dataCheckingQuery = false;
       }
        
        function loadOldQueries() {
        	
        	queryService.getAll(vm.maxOldQueries.selectedOption.value)
    		.then(function (data) {
    			if(data.success===true)
    			{
    				vm.oldTasks = [];
    				vm.oldQueries = data.queries;
    				//get tasks in linear structure
    				angular.forEach(data.queries, function(query) {
    					angular.forEach(query.tasks, function(task) {
    						task.queryId = query.id
        					vm.oldTasks.push(task);
    						
        				}
        				);
    				}
    				);
    			}
    	});
        }
        
     }]);
});