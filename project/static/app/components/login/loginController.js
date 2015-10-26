'use strict';

define(['app'], function (app) {

    
    app.register.controller('loginController', ['$location', 'AuthenticationService', 'FlashService', 
     function ($location, AuthenticationService, FlashService) {

        var vm = this;

        vm.login = login;

        (function initController() {
            // reset login status
            AuthenticationService.ClearCredentials();
        })();

        function login() {
            vm.dataLoading = true;
            AuthenticationService.Login(vm.username, vm.password, function (response) {
                
                if (response.success===true) {
                    AuthenticationService.SetCredentials(vm.username, vm.password, response.userid, response.firstname, response.lastname);
                    $location.path('/manageKeys');
                } else {
                    FlashService.Error(response.message);
                    vm.dataLoading = false;
                }
            });
        };


     }]);
});
