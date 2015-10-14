//'use strict';

define(['app'], function (app) {

    
    app.register.controller('fetchController', ['UserService', '$rootScope', 
     function (UserService, $rootScope) {

        var vm = this;

        vm.user = null;
        vm.allUsers = [];
        vm.deleteUser = deleteUser;

        //initController();

        function initController() {
            loadCurrentUser();
            //loadAllUsers();
        }

        function loadCurrentUser() {
            UserService.GetById($rootScope.globals.currentUser.id)
                .then(function (user) {
                    vm.user = user
                });
        }
/*
        function loadAllUsers() {
            UserService.GetAll()
                .then(function (users) {
                    vm.allUsers = users;
                });
        }
        */

        function deleteUser(id) {
            UserService.Delete(id)
            .then(function () {
                loadAllUsers();
            });
        }


     }]);
});