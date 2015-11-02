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
        $scope.categoriesChartOptions = {
            seriesDefaults : {
                // use the pie chart renderer
                renderer : jQuery.jqplot.PieRenderer,
                rendererOptions : {
                    // Put data labels on the pie slices.
                    // By default, labels show the percentage of the slice.
                    showDataLabels : true
                }
            },
            legend: {
                show: true,
                rendererOptions: {
                    
                },
                location: 'w'
            }
        };

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
        
        var vm = this;
        vm.sortType = 'intersection'
        vm.loadOldQueries = loadOldQueries;
        vm.changeToResult = changeToResult;
        vm.loadAdditionalData = loadAdditionalData;
        vm.oldTasks = [];
        vm.oldQueries = [];
        vm.result = [];
        vm.result.viewCount = null;
        vm.result.commentCount = null;
		vm.result.likeCount = null;
		vm.result.dislikeCount = null;
		vm.result.dashRepresentation = null;
        $scope.plot = [];
        $scope.plot.publishedAt = [];
        $scope.plot.category = [];
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
            	loadResults("summary");
            	loadResults("intersection");
            	loadResults("category");
            	
            	vm.loadedResult =  $routeParams.id;
            }
        }
        
        function changeToResult(id) {
        	$location.path("/result/"+id)
        }
        
        function loadResults(section) {
        	vm.loadedResult = false
        	resultService.getResults($routeParams.id,section)
        		.then(function (data) {
        			if(data.success===true)
        			{
        				
        				vm.loadedResult = $routeParams.id;
        				if(section=="intersection") {
        					vm.result.intersection = data.statistics
        				}
        				if(section=="dash_representations") {
        					vm.result.dashRepresentation = data.statistics;
        				}
        				if(section=="publishedAt" && !vm.result.publishedAt) {
        					vm.result.publishedAt = data.statistics;
        					vm.temp = [];
            				angular.forEach(vm.result.publishedAt,function(day){
            					vm.temp.push([day.date,day.count]);
            				});
            				
            				$scope.plot.publishedAt.push(vm.temp);
        				}
        				
        				if(section=="statistics_viewCount" && !vm.result.viewCount) {
        					vm.result.viewCount = data.statistics.statistics_viewCount
        				}
        				if(section=="statistics_commentCount" && !vm.result.commentCount) {
        					vm.result.commentCount = data.statistics.statistics_commentCount
        				}
        				if(section=="statistics_likeCount" && !vm.result.likeCount) {
        					vm.result.likeCount = data.statistics.statistics_likeCount
        				}
        				if(section=="statistics_dislikeCount" && !vm.result.dislikeCount) {
        					vm.result.dislikeCount = data.statistics.statistics_dislikeCount
        				}
        				if(section=="summary") {
        					vm.result.summary = data.statistics
        				}
        				if(section=="category") {
        					vm.result.category = data.statistics
        					vm.temp = [];
            				angular.forEach(vm.result.category,function(category){
            					vm.temp.push([category.id+" "+category.name,category.count]);
            				});
            				
            				$scope.plot.category.push(vm.temp);
        				}
        				
        			} else {
        				vm.loadedResult = false
        				vm.result.error = "could not fetch result from server";
        			}
        		});
        }
        
        function loadAdditionalData(section) {
        	
        	if(section=="publishedAt" && !vm.result.publishedAt) {
				loadResults(section);
			}
        	
        	if(section=="statistics_viewCount" && !vm.result.viewCount) {
				loadResults(section);
			}
        	if(section=="statistics_commentCount" && !vm.result.commentCount) {
				loadResults(section);
			}
        	if(section=="statistics_likeCount" && !vm.result.likeCount) {
				loadResults(section);
			}
        	if(section=="statistics_dislikeCount" && !vm.result.dislikeCount) {
				loadResults(section);
			}
        	if(section=="dash_representations" && !vm.result.dashRepresentation) {
				loadResults(section);
			}
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