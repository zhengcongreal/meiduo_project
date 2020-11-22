var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: '',
        olist: [],
        page: 1, // 当前页数
        page_size: 5, // 每页数量
        sku_list:[],
        count: 0,
    },

    computed: {
        total_page: function(){  // 总页数
            // return Math.ceil(this.count/this.page_size);
            return this.count;
        },
        next: function(){  // 下一页
            if (this.page >= this.total_page) {
                return 0;
            } else {
                return this.page + 1;
            }
        },
        previous: function(){  // 上一页
            if (this.page <= 0 ) {
                return 0;
            } else {
                return this.page - 1;
            }
        },
        page_nums: function(){  // 页码
            // 分页页数显示计算
            // 1.如果总页数<=5
            // 2.如果当前页是前3页
            // 3.如果当前页是后3页,
            // 4.既不是前3页，也不是后3页
            var nums = [];
            if (this.total_page <= 5) {
                for (var i=1; i<=this.total_page; i++){
                    nums.push(i);
                }
            } else if (this.page <= 3) {
                nums = [1, 2, 3, 4, 5];
            } else if (this.total_page - this.page <= 2) {
                for (var i=this.total_page; i>this.total_page-5; i--) {
                    nums.push(i);
                }
            } else {
                for (var i=this.page-2; i<this.page+3; i++){
                    nums.push(i);
                }
            }
            return nums;
        }
    },

    mounted: function () {
        // 获取cookie中的用户名
        this.username = getCookie('username');

        // 获取个人订单信息:
        this.get_personal_orders();


    },
    methods: {
              // 退出登录按钮
        logoutfunc: function () {
            var url = this.host + '/logout/';
            axios.delete(url, {
                responseType: 'json',
                withCredentials:true,
            })
                .then(response => {
                    location.href = 'login.html';
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
          // 点击页数
        on_page: function(num){
            if (num != this.page){
                this.page = num;
                this.get_personal_orders();
            }
        },
        get_personal_orders:function(){
             // 添加下列代码, 发送请求, 获取用户的浏览记录信息:
            axios.get(this.host + '/orders/get_personal_orders/',
                {
                      params: {
                        page: this.page,
                        page_size: this.page_size,

                    },
                    responseType: 'json',
                    withCredentials:true,
                })
                .then(response => {
                    if (response.data.code == 400) {
                        location.href = 'login.html'
                        return
                    }
                    this.olist = response.data.orders;
                    this.count=response.data.count;
                    console.log(this.olist[0].sku_orders[0].sku_name);
                    console.log(this.olist)
                    // this.histories = response.data.skus;
                    // for(var i=0; i<this.histories.length; i++){
                    //   this.histories[i].url='/goods/'+this.histories[i].id + '.html';
                    // }
                })
                .catch(error => {
                    console.log(error)
                });
        },
    }
});