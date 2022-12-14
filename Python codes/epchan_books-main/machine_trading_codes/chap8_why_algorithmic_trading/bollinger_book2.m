clear;

% 1 minute data on GLD-USO
% load('inputData_ETF', 'tday', 'syms', 'cl');
load('inputDataOHLCDaily_ETF_20160401', 'tday', 'stocks', 'cl');

idxG=find(strcmp('GLD', stocks));
idxU=find(strcmp('USO', stocks));

x=cl(:, idxG);
y=cl(:, idxU);

lookback=20; % Lookback set arbitrarily short
hedgeRatio=NaN(size(x, 1), 1);
for t=lookback:size(hedgeRatio, 1)
    regression_result=ols(y(t-lookback+1:t), [x(t-lookback+1:t) ones(lookback, 1)]);
    hedgeRatio(t)=regression_result.beta(1);
end

y2=[x y];

yport=sum([-hedgeRatio ones(size(hedgeRatio))].*y2, 2); % The net market value of the portfolio is same as the "spread"
% hedgeRatio(1:lookback)=[]; % Removed because hedge ratio is indterminate
% yport(1:lookback)=[]; 
% y2(1:lookback, :)=[];
% 
% Bollinger band strategy
entryZscore=1;
exitZscore=0;

MA=movingAvg(yport, lookback);
MSTD=movingStd(yport, lookback);
zScore=(yport-MA)./MSTD;

longsEntry=zScore < -entryZscore; % a long position means we should buy EWC
longsExit=zScore > -exitZscore;

shortsEntry=zScore > entryZscore;
shortsExit=zScore < exitZscore;

numUnitsLong=NaN(length(yport), 1);
numUnitsShort=NaN(length(yport), 1);

numUnitsLong(1)=0;
numUnitsLong(longsEntry)=1; 
numUnitsLong(longsExit)=0;
numUnitsLong=fillMissingData(numUnitsLong); % fillMissingData can be downloaded from epchan.com/book2. It simply carry forward an existing position from previous day if today's positio is an indeterminate NaN.

numUnitsShort(1)=0;
numUnitsShort(shortsEntry)=-1; 
numUnitsShort(shortsExit)=0;
numUnitsShort=fillMissingData(numUnitsShort);

numUnits=numUnitsLong+numUnitsShort;
positions=repmat(numUnits, [1 size(y2, 2)]).*[-hedgeRatio ones(size(hedgeRatio))].*y2; % [hedgeRatio -ones(size(hedgeRatio))] is the shares allocation, [hedgeRatio -ones(size(hedgeRatio))].*y2 is the dollar capital allocation, while positions is the dollar capital in each ETF.
pnl=sum(lag(positions, 1).*(y2-lag(y2, 1))./lag(y2, 1), 2); % daily P&L of the strategy
ret=pnl./sum(abs(lag(positions, 1)), 2); % return is P&L divided by gross market value of portfolio
ret(isnan(ret))=0;

% figure;
testset=find(tday>20120409);
plot(datetime(tday(testset), 'ConvertFrom', 'yyyyMMdd'), cumprod(1+ret(testset))-1); % Cumulative compounded return

fprintf(1, 'APR=%f Sharpe=%f\n', prod(1+ret(testset)).^(252/length(ret(testset)))-1, sqrt(252)*mean(ret(testset))/std(ret(testset)));
% APR=0.078994 Sharpe=0.565015

