var app = angular.module('app', ['ngRoute', 'mgcrea.ngStrap', 'ngSanitize'])
	.config(function($interpolateProvider){
	    $interpolateProvider.startSymbol('[[').endSymbol(']]');
	})
	.config(['$routeProvider', function($routeProvider) {
	    $routeProvider
	    .when('/', {
	        controller: 'RoomListController',
	        controllerAs: 'list',
	        templateUrl: 'static/list.html'
	    })
	    .when('/rooms/:roomName', {
	        controller: 'RoomController',
	        controllerAs: 'room',
	        templateUrl: 'static/detail.html'
	    });
	}])
    .controller('RoomController',['$http', '$routeParams','$scope', '$interval', '$rootScope',
     function($http, $routeParams, $scope, $interval, $rootScope){
        console.log($routeParams);
        var value = this;
        value.title = [];


        $scope.loadRoom = function() {
            $http.get('/api/rooms/' + $routeParams.roomName).success(function(data){
                value.title=data;
                value.data = data;
                $scope.the_room = data;
                $rootScope.roomSlug = data.slug;
            })
            .error(function(data){
                //Should go to 404
                //$location.path('/404'); possibly
            });
        };

        $rootScope.loadRoom = $scope.loadRoom;

        this.join = function(queueSlug) {
            $http.post('/api/queues/' + queueSlug + '/join/')
            .success( function(data) {
                $scope.loadRoom();
            });
        };
        this.openQueue = function(queue) {
            $rootScope.openQueue = queue;
        };

        var promise = $interval( $scope.loadRoom, 30000);

        $scope.loadRoom();

        $scope.$on('$destroy', function() {
            if(angular.isDefined(promise)) {
                $interval.cancel(promise);
                promise = undefined;
            }
        });

    }])
    .controller('NewRoomController', ['$scope', '$http', function($scope, $http) {
        $scope.submit = function(newroom) {
            $http.post('/api/rooms/', {
                data: newroom
            }).success(function() {
                location.reload();
            });
        };
    }])
    .controller('NewQueueController', ['$scope', '$http', '$routeParams','$rootScope',
     function($scope, $http, $routeParams, $rootScope) {
        $scope.submit = function(newqueue) {
            $http.post('/api/rooms/' + $rootScope.roomSlug + '/queues/', {
                data: newqueue
            }).success(function() {
                $rootScope.loadRoom();
            });
        };
    }])
    .controller('RoomListController', ['$http', function($http){
        var value = this;
        $http.get('/api/rooms/').success(function(data){
            value.data = data;
        });
    }])
    .controller('ResourceController', ['$http', '$scope', function($http, $scope){

        $scope.queue_element = $scope.resource.current_queue_element;

    }])
    .controller('EditRoomController', ['$http', '$scope', '$rootScope', '$location', function($http, $scope, $rootScope, $location){
        $scope.newMember = function() {
            $rootScope.editingRoom.newMembers.push({})
        };
        $scope.deleteMember = function(member_id) {
            $scope.editingRoom.deletedMembers.push(member_id);
            $scope.editingRoom.members = $scope.editingRoom.members.filter(function(member) {
                return member._id !== member_id;
            });
        };
        $scope.openRoom = function() {
            $rootScope.editingRoom = angular.copy($scope.the_room);
            $rootScope.editingRoom.deletedMembers = [];
            $rootScope.editingRoom.newMembers = [];
        };

        $scope.delete = function(room) {
            $http.delete('/api/rooms/' + room.slug + '/')
            .success( function(data) {
                $location.path('/');
            });
        };

        $scope.submit = function(room) {
            $http.post('/api/rooms/' + room.slug + '/',{
                data: room
            })
            .success(function(){
                $rootScope.loadRoom();
            });
        };
    }])
    .controller('EditQueueController', ['$http', '$scope','$rootScope', function($http, $scope, $rootScope){

        $scope.newResource = function() {
            $rootScope.editingQueue.resources.push({isNew: true});
        };
        $scope.deleteResource = function(resource_id) {
            $scope.editingQueue.deletedResources.push(resource_id);
            $scope.editingQueue.resources = $scope.editingQueue.resources.filter(function(resource) {
                return resource._id !== resource_id;
            });
        };
        $scope.submit = function(queue) {
            $http.post('/api/rooms/' + $rootScope.roomSlug + '/queues/' + queue._id + '/',
            {
                data: queue
            })
            .success(function() {
                $scope.loadRoom();
            });
            console.log(queue);
        };

        $scope.delete = function(queue) {
            $http.delete('/api/rooms/' + $rootScope.roomSlug + '/queues/' + queue._id + '/')
            .success(function() {
                $scope.loadRoom();
            });
        };

        $scope.openQueue = function(queue) {
            $rootScope.editingQueue = angular.copy(queue);
            $rootScope.editingQueue.deletedResources = [];
        };
    }])
    .controller('QueueElementController', ['$http', '$scope', function($http, $scope){

        $scope.delete = function() {
            $http.delete('/api/queues/' + $scope.queue._id + '/queue_elements/' + $scope.queue_element._id).success( function(){
                $scope.loadRoom();
            });
        };

    }])
    .directive("customPopover", ["$popover", "$compile", function($popover, $compile) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var myPopover = $popover(element, {
                    title: 'My Title',
                    contentTemplate: 'example.html',
                    html: true,
                    trigger: 'manual',
                    autoClose: true,
                    scope: scope
                });
                scope.showPopover = function() {
                    myPopover.show();
                }
            }
        }
    }]);
