'use strict';
angular.module('ui.chart', []).directive('uiChart', function() {
    return {
        restrict : 'EACM',
        template : '<div></div>',
        replace : true,
        link : function(scope, elem, attrs) {
            var renderChart = function() {
                var data = scope.$eval(attrs.uiChart);
                elem.html('');
                if (!angular.isArray(data)) {
                    return;
                }

                var opts = {};
                if (!angular.isUndefined(attrs.chartOptions)) {
                    opts = scope.$eval(attrs.chartOptions);
                    if (!angular.isObject(opts)) {
                        throw 'Invalid ui.chart options attribute';
                    }
                }

                elem.jqplot(data, opts);
            };

            scope.$watch(attrs.uiChart, function() {
                renderChart();
            }, true);

            scope.$watch(attrs.chartOptions, function() {
                renderChart();
            });
        }
    };
});
define(['app'], function (app) {


    
    app.register.controller('resultController', ['queryService','resultService','$scope', '$rootScope','$routeParams','$location','$timeout','$filter',
     function (queryService,resultService, $scope, $rootScope, $routeParams, $location, $timeout,$filter,charting) {

    	//pie chart data - scope
        $scope.pieChartData = [[['Chris', 12], ['Manuel', 9], ['Dustin', 14], ['Anu', 16], ['Vijay', 7], ['El Luchadore', 9]]];

        //donut chart data - scope
        $scope.donutChartData = [[['Hawaii', 6], ['Boston', 8], ['Japan', 14], ['Russia', 20]], [['Hawaii', 8], ['Boston', 12], ['Japan', 6], ['Russia', 9]]];

        //stacked barchart data - scope
        
        $scope.publishedAt = [[['2008-10-10',4], ['2008-10-11',6.5], ['2008-10-12',5.7], ['2008-10-13',9], ['2008-10-14',8.2]]];
        
        $scope.bubbleChartData = [[11, 123, 1236, "Acura"], [45, 92, 1067, "Alfa Romeo"],[24, 104, 1176, "AM General"], [50, 23, 610, "Aston Martin Lagonda"],[18, 17, 539, "Audi"], [7, 89, 864, "BMW"], [2, 13, 1026, "Bugatti"]];

        // pie chart options - scope
        $scope.pieChartOptions = {
            seriesDefaults : {
                // use the pie chart renderer
                renderer : jQuery.jqplot.PieRenderer,
                rendererOptions : {
                    // Put data labels on the pie slices.
                    // By default, labels show the percentage of the slice.
                    showDataLabels : true
                }
            },
            legend : {
                show : true,
                location : 'e'
            }
        };

        // donut chart options - scope
        $scope.donutChartOptions = {
            seriesDefaults : {
                // use the donut chart renderer
                renderer : jQuery.jqplot.DonutRenderer,
                rendererOptions : {
                    sliceMargin : 3,
                    // Pies and donuts can start at any arbitrary angle.
                    startAngle : -90,
                    showDataLabels : true
                }
            },
            legend : {
                show : true,
                location : 'e'
            }
        };

        // bar chart options - scope
        $scope.publishedAtChartOptions = {
        		seriesDefaults : {
                    // use the bar chart renderer
                    renderer : $.jqplot.LineRenderer,
                    rendererOptions : {
                       
                    },
                    
                    
                },
                axes: {
                    xaxis: {
                        renderer: $.jqplot.DateAxisRenderer,
                        tickOptions:{formatString:'%b %#d'},
                        tickInterval:'2 days'
                    }
                }
                
        };
        
        $scope.bubbleChartOptions = {
            seriesDefaults : {
                // use the donut chart renderer
                renderer : jQuery.jqplot.BubbleRenderer,
                rendererOptions : {
                    bubbleAlpha: 0.7,
                    varyBubbleColors: false
                }
            },
            shadow: true
        };
        
        var vm = this;
        vm.sortType = 'intersection'
        vm.loadOldQueries = loadOldQueries;
        vm.createTask = createTask;
        vm.changeToResult = changeToResult;
        vm.oldTasks = [];
        vm.oldQueries = [];
        
    
        $scope.plot = [];
        $scope.plot.publishedAt = [];
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
        	
            loadOldQueries();
            if(typeof $routeParams.id !== 'undefined') {
            	loadResults();
            	vm.loadedResult =  $routeParams.id;
            }
        }
        
    
      
        vm.someData = [[
                            ['Heavy Industry', 12],['Retail', 9], ['Light Industry', 14],
                            ['Out of home', 16],['Commuting', 7], ['Orientation', 9]
                          ]];

                         
        
        function changeToResult(id) {
        	$location.path("/result/"+id)
        }
        
        function loadResults() {
        	vm.loadedResult = false
        	resultService.getResults($routeParams.id,false)
        		.then(function (data) {
        			if(data.success===true)
        			{
        				vm.result = data.statistics;
        				vm.loadedResult = $routeParams.id;
        				vm.temp = [];
        				angular.forEach(vm.result.data.day_histogram,function(day){
        					vm.temp.push([day.date,day.count]);
        				});
        				
        				$scope.plot.publishedAt.push(vm.temp);

        			} else {
        				vm.loadedResult = false
        				vm.result.error = "could not fetch result from server";
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