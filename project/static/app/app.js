//'use strict';

define(['shared/services/routeResolver'], function () {

    var app = angular.module('youtubeApp', ['ngRoute', 'routeResolverServices', 'ngCookies', 'ui.bootstrap','ngSanitize','ui.select','ui.chart']);

    app.config(['$routeProvider', 'routeResolverProvider', '$controllerProvider',
                '$compileProvider', '$filterProvider', '$provide', '$httpProvider',

        function ($routeProvider, routeResolverProvider, $controllerProvider,
                  $compileProvider, $filterProvider, $provide, $httpProvider) {
    		
    		//default convert received date string into javascript date objects
	    	$httpProvider.defaults.transformResponse.push(function(responseData){
	            convertDateStringsToDates(responseData);
	            return responseData;
	        });
	    	var regexIso8601 = /(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))/;

	    	function convertDateStringsToDates(input) {
	    	    // Ignore things that aren't objects.
	    	    if (typeof input !== "object") return input;

	    	    for (var key in input) {
	    	        if (!input.hasOwnProperty(key)) continue;

	    	        var value = input[key];
	    	        var match;
	    	        // Check for string properties which look like dates.
	    	        if (typeof value === "string" && (match = value.match(regexIso8601))) {
	    	            var milliseconds = Date.parse(match[0])
	    	            if (!isNaN(milliseconds)) {
	    	                input[key] = new Date(milliseconds);
	    	            }
	    	        } else if (typeof value === "object") {
	    	            // Recurse into object
	    	            convertDateStringsToDates(value);
	    	        }
	    	    }
	    	}
    	
            //Change default views and controllers directory using the following:
            //routeResolverProvider.routeConfig.setBaseDirectories('/app/views', '/app/controllers');

            app.register =
            {
                controller: $controllerProvider.register,
                directive: $compileProvider.directive,
                filter: $filterProvider.register,
                factory: $provide.factory,
                service: $provide.service
            };

            //Define routes - controllers will be loaded dynamically
            var route = routeResolverProvider.route;

            $routeProvider
                //route.resolve() now accepts the convention to use (name of controller & view) as well as the 
                //path where the controller or view lives in the controllers or views folder if it's in a sub folder. 
                //For example, the controllers for customers live in controllers/customers and the views are in views/customers.
                //The controllers for orders live in controllers/orders and the views are in views/orders
                //The second parameter allows for putting related controllers/views into subfolders to better organize large projects
                //Thanks to Ton Yeung for the idea and contribution
                .when('/',{
                    templateUrl: 'static/app/components/home/homeView.html'
                })
                
                .when('/login',route.resolve('login','login/', 'vm'))
                .when('/register',route.resolve('register','register/', 'vm'))
                .when('/manageKeys',route.resolve('manageKeys','manageKeys/', 'vm', true))
                .when('/query',route.resolve('query','query/', 'vm', true))
                .when('/query/:id',route.resolve('query','query/', 'vm', true))
                .when('/task',route.resolve('task','task/', 'vm', true))
                .when('/task/:id',route.resolve('task','task/', 'vm', true))
                .when('/task/:id/:action',route.resolve('task','task/', 'vm', true))
                .when('/result/:id',route.resolve('result','result/', 'vm', true))
                .when('/result',route.resolve('result','result/', 'vm', true))
                
                .otherwise({ redirectTo: '/' });

    }]);

   

    app.run(['$rootScope', '$location', '$cookieStore', '$http',
        function ($rootScope, $location, $cookieStore, $http) {
            
            // keep user logged in after page refresh
            $rootScope.globals = $cookieStore.get('globals') || {};
            if ($rootScope.globals.currentUser) {
                //$http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.currentUser.authdata;
            }

            //Client-side security. Server-side framework MUST add it's 
            //own security as well since client-based security is easily hacked
            $rootScope.$on("$routeChangeStart", function (event, next, current) {
                if (next && next.$$route && next.$$route.secure) {
                    if (!$rootScope.globals.currentUser) {
                        $location.path('/login');
                    }
                }
            });

    }]);



    return app;

});




