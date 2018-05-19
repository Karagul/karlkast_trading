//+------------------------------------------------------------------+
//|                                           LLC.data.RLearning.mq5 |
//|                                                      Karl Lilley |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Karl Lilley"
#property link      "https://www.mql5.com"
#property version   "1.00"

#define SIZE 55

int    fileHandle=-1;
double avgBuyArray[SIZE];
double avgSellArray[SIZE];
double avgSpread[SIZE];
double avgBuyDiff[SIZE];
double avgSellDiff[SIZE];
int      avgTickPerMinute[SIZE];
int    size=SIZE;
double prevBuy=0;
double prevSell=0;
double prevAvgBuy=0;
double prevAvgSell=0;
uint   prevTimeSinceEpoc=0;
int    avgIndex=0;
int    ticksPerMinute=0;
uint   tickCounterSeconds=0;
int    tickAvgIndex=0;
int    currentMonth;
int    buyPointsMonthTotal;
int    sellPointsMonthTotal;
int    buyAvgPointsMonthTotal;
int    sellAvgPointsMonthTotal;
int    totalMinutePressure;
int    totalMonthPressure;
bool   isFirstMonthTick;
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   FileClose(fileHandle);
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   double buy=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double sell=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   MqlDateTime timeStr;
   datetime tickTime=TimeCurrent();
   TimeToStruct(tickTime,timeStr);
   uint timeSinceEpoc=(uint)tickTime;
   if(buy>0 && sell>0)
     {
      double avgBuy=getAvg(avgBuyArray);
      double avgSell=getAvg(avgSellArray);
      double spread=buy-sell;

      double prevBuyDiff=buy-prevBuy;
      double prevSellDiff=sell-prevSell;
      double prevAvgBuyDiff=avgBuy-prevAvgBuy;
      double prevAvgSellDiff=avgSell-prevAvgSell;

      uint timeDiff=timeSinceEpoc-prevTimeSinceEpoc;

      openNewFile(timeStr.mon,timeStr.year);

      if(prevBuy>0 && prevSell>0 && !isFirstMonthTick)
        {
         if(timeSinceEpoc-tickCounterSeconds>60)
           {
            totalMinutePressure=0;
            ticksPerMinute=0;
            tickCounterSeconds=timeSinceEpoc;
            tickAvgIndex++;
           }
         ticksPerMinute++;
         if(avgIndex>size && tickAvgIndex>size)
           {
            if(prevAvgBuy==0 && prevAvgSell==0)
              {
               prevAvgBuy=avgBuy;
               prevAvgSell=avgSell;
              }

            //points diff/total
            int prevBuyDiffPoints=getPointsInt(prevBuyDiff);
            int prevSellDiffPoints=getPointsInt(prevSellDiff);
            buyPointsMonthTotal+=prevBuyDiffPoints;
            sellPointsMonthTotal+=prevSellDiffPoints;

            //avg points diff/total
            int prevAvgBuyDiffPoints=getPointsInt(prevAvgBuyDiff);
            int prevAvgSellDiffPoints=getPointsInt(prevAvgSellDiff);
            buyAvgPointsMonthTotal+=prevAvgBuyDiffPoints;
            sellAvgPointsMonthTotal+=prevAvgSellDiffPoints;

            //pressure for buys/sells per/[something undecided]
            totalMinutePressure+=prevBuyDiffPoints==0 ? 0 :(prevBuyDiffPoints>0 ? 1 : -1);
            totalMonthPressure +=prevBuyDiffPoints==0 ? 0 :(prevBuyDiffPoints>0 ? 1 : -1);



            //write out data to file
            FileWrite(fileHandle,
                      tickTime,//Timestamp
                      IntegerToString(timeStr.hour),//hour
                      IntegerToString(timeStr.mon), //Month
                      getPoints(buy),//buy
                      buyPointsMonthTotal,//buyTotal
                      getPoints(sell),//sell
                      sellPointsMonthTotal,//sellTotal
                      getPoints(spread),//spread
                      MathAbs(prevBuyDiffPoints),//prevBuyDiff
                      MathAbs(prevSellDiffPoints),//prevSellDiff
                      prevBuyDiffPoints>0 ? 1 : 0,//isBuy
                      totalMinutePressure,//buy/sell pressure
                      totalMonthPressure,
                      getPoints(avgBuy),//avgBuy
                      //buyAvgPointsMonthTotal,//avgBuyTotal
                      getPoints(avgSell),//avgSell
                      //sellAvgPointsMonthTotal,//avgSellTotal
                      //getPoints(getAvg(avgSpread)),//avgSpread
                      //prevAvgBuyDiffPoints, //avgBuyDiff
                      //sellAvgPointsMonthTotal, //avgSellDiff
                      IntegerToString(ticksPerMinute),//ticksPerMinute
                      //IntegerToString(getAvg(avgTickPerMinute)),//avgTicksPerMinute
                      IntegerToString(timeDiff) //timeDiff
                      );
            setupAvgs(buy,sell,spread,prevBuyDiff,prevSellDiff,ticksPerMinute);
           }
         else
           {
            setupAvgs(buy,sell,spread,prevBuyDiff,prevSellDiff,ticksPerMinute);
           }
        }
      else
        {
         setupAvgs(buy,sell,spread,prevBuyDiff,prevSellDiff,ticksPerMinute);
        }
      isFirstMonthTick=false;
      avgIndex++;
      prevBuy=buy;
      prevSell=sell;
      prevTimeSinceEpoc=timeSinceEpoc;
     }
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void setupAvgs(double buy,double sell,double spread,double buyDiff,double sellDiff,int tPerMin)
  {
   avgBuyArray[avgIndex%size]=buy;
   avgSellArray[avgIndex%size]=sell;
   avgSpread[avgIndex%size]=spread;
//avgBuyDiff[avgIndex%size]=MathAbs(buyDiff);
//avgSellDiff[avgIndex%size]=MathAbs(sellDiff);
   avgTickPerMinute[tickAvgIndex%size]=tPerMin;
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double getAvg(double &avgArray[])
  {
   int count=ArraySize(avgArray);
   double total=0;
   for(int i=0; i<count; i++)
     {
      total+=avgArray[i];
     }
   return total/count;
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int getAvg(int &avgArray[])
  {
   int count=ArraySize(avgArray);
   int total=0;
   for(int i=0; i<count; i++)
     {
      total+=avgArray[i];
     }
   return total/count;
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
string getPoints(double value)
  {
   int points=0;
   double normalized=NormalizeDouble(value,5);

   if(_Symbol=="EURUSD")
     {
      points=(int)(normalized*100000);
     }

   return IntegerToString(points);
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int getPointsInt(double value)
  {
   int points=0;
   double normalized=NormalizeDouble(value,5);

   if(_Symbol=="EURUSD")
     {
      points=(int)(normalized*100000);
     }

   return points;
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void openNewFile(int month,int year)
  {
   if(fileHandle==-1 || month!=currentMonth)
     {
      currentMonth=month;
      FileClose(fileHandle);
      string fileName=StringFormat("RLearning.%s.%d.%d.data.csv",_Symbol,month,year);
      fileHandle=FileOpen(fileName,FILE_WRITE|FILE_CSV|FILE_ANSI,',');
      FileWrite(fileHandle,"sep=,");
      FileWrite(fileHandle,
                "Timestamp",
                "Hour",
                "Month",
                "buy",
                "buyTotal",
                "sell",
                "sellTotal",
                "spread",
                "prevBuyDiff",
                "prevSellDiff",
                "isBuy",
                "totalMinutePressure",
                "totalMonthPressure",
                "avgBuy",
                //"avgBuyTotal",
                "avgSell",
                //"avgSellTotal",
                //"avgSpread",
                //"avgBuyDiff",
                //"avgSellDiff",
                "ticksPerMinute",
                //"avgTicksPerMinute",
                "timeDiff"
                );
      buyPointsMonthTotal=0;
      sellPointsMonthTotal=0;
      sellAvgPointsMonthTotal= 0;
      buyAvgPointsMonthTotal = 0;
      totalMonthPressure=0;
      isFirstMonthTick=true;
     }
  }
//+------------------------------------------------------------------+
