/**
 * Created by hfy on 18/4/8.
 */
export function getCookie (name) {
  if (document.cookie.length>0)

  {

    let tmp_cookie = document.cookie,

      tmp_c1 = (tmp_cookie.indexOf(" "+name+"=")>0) ? (tmp_cookie.indexOf(" "+name+"=")+1) : 0,

      tmp_c2 = (tmp_cookie.indexOf(";"+name+"=")>0) ? (tmp_cookie.indexOf(";"+name+"=")+1) : 0,

      tmp_c3 = (tmp_cookie.indexOf(name+"=")===0) ? 0 : -1,

      c_start=tmp_c1 || tmp_c2 || tmp_c3;

    if (c_start!==-1)

    {

      c_start=c_start + name.length+1;

      let c_end=tmp_cookie.indexOf(";",c_start);

      if (c_end===-1) c_end=tmp_cookie.length;

      return (tmp_cookie.substring(c_start,c_end));

    }

  }

  return "";
}

export function setCookie(name, value, day) {

  if (day !== 0) { //当设置的时间等于0时，不设置expires属性，cookie在浏览器关闭后删除

    let exp = new Date();
    exp.setTime(exp.getTime() + day * 24 * 60 * 60 * 1000);
    document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();

  } else {

    document.cookie = name + "=" + escape(value);

  }

};

export function delCookie (name) {
    let exp = new Date()
    exp.setTime(exp.getTime() - 10000)
    let cval = getCookie(name);
    if(cval!=null)
      document.cookie= name + "="+cval+";expires="+exp.toGMTString();

}

