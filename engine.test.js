const test=require('node:test'),assert=require('node:assert/strict');const {execution,outcome,signal}=require('./server');
test('flat price costs 1.10 on both sides',()=>{assert.equal(outcome('UP',80000,80000),-1.1);assert.equal(outcome('DOWN',80000,80000),-1.1)});
test('profitable direction after costs',()=>{assert.ok(outcome('UP',80000,80800)>8);assert.ok(outcome('DOWN',80000,79200)>8)});
test('adverse move loses',()=>{assert.ok(outcome('UP',80000,79200)<-10);assert.ok(outcome('DOWN',80000,80800)<-10)});
test('fees and adverse fill',()=>{const x=execution('UP',80000,80000);assert.ok(x.fees>0);assert.ok(x.entryFill>x.exitFill)});
test('warmup',()=>assert.equal(signal([1,2,3]),'WAIT'));
