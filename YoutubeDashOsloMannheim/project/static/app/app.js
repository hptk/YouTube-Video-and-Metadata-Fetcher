//'use strict';

define(['shared/services/routeResolver'], function () {

    var app = angular.module('youtubeApp', ['ngRoute', 'routeResolverServices', 'ngCookies', 'ui.bootstrap']);

    app.config(['$routeProvider', 'routeResolverProvider', '$controllerProvider',
                '$compileProvider', '$filterProvider', '$provide', '$httpProvider',

        function ($routeProvider, routeResolverProvider, $controllerProvider,
                  $compileProvider, $filterProvider, $provide, $httpProvider) {

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
                .when('/query/:hash',route.resolve('query','query/', 'vm', true))
                
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




