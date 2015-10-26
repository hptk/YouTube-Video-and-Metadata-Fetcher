'use strict';

define(['app'], function (app) {

    
    app.register.controller('resultController', ['APIKeyService','queryService','taskService', '$rootScope','$routeParams','$location','$timeout','$filter',
     function (APIKeyService,queryService,taskService, $rootScope, $routeParams, $location, $timeout,$filter,charting) {

        var vm = this;
        
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
        
        vm.taskOptions = [
							{ name: 'Fetches only the Video IDs for the selected query' , type:'IDFetcher'},
							{ name: 'Fetches the meta data for the videos which are associated with the selected query' , type:'MetaFetcher'},
							{ name: 'Download the videos which are associated with the selected query' , type:'VideoFetcher'}
                      ];
        
        
        initController();
        
        
        function initController() {
        	
            loadOldQueries();
            if(typeof $routeParams.id !== 'undefined') {
            	loadHashQuery();
            }
        }
        
        
        vm.someData = [[
                            ['Heavy Industry', 12],['Retail', 9], ['Light Industry', 14],
                            ['Out of home', 16],['Commuting', 7], ['Orientation', 9]
                          ]];

                          //vm.myChartOpts = charting.pieChartOptions
        
        
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
    	   taskService.createTask(id,action)
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
  						
  					
  					if (data.state != 'PENDING' && data.state != 'PROGRESS' && data.state!='SAVING') {
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