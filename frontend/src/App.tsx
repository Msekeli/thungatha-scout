import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "./supabase";
export default function App() {
 const [session,setSession]=useState<Session|null>(null); const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [error,setError]=useState("");
 useEffect(()=>{ if(!supabase)return; supabase.auth.getSession().then(({data})=>setSession(data.session)); const {data}=supabase.auth.onAuthStateChange((_event,value)=>setSession(value)); return ()=>data.subscription.unsubscribe(); },[]);
 async function signIn(event:FormEvent<HTMLFormElement>){event.preventDefault();if(!supabase)return;const result=await supabase.auth.signInWithPassword({email,password});setError(result.error?.message??"");}
 if(!supabase)return <main className="panel"><h1>Scout setup required</h1><p>Set the Supabase URL and anon key in frontend/.env.local.</p></main>;
 return <main className="panel"><p className="eyebrow">THUNGATHA SCOUT</p>{session?<><h1>Scout admin</h1><p>Signed in as {session.user.email}</p><button onClick={()=>supabase.auth.signOut()}>Sign out</button><p>Admin modules will be added in M5.</p></>:<><h1>Admin sign in</h1><form onSubmit={signIn}><label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} required/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/></label><button type="submit">Sign in</button></form></>}{error&&<p role="alert">{error}</p>}</main>;
}
