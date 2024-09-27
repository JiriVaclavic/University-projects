-- Soubor:	flp-fun.hs
-- Datum:	31.3.2024
-- Autor:	Bc. Jiri Vaclavic, xvacla31@stud.fit.vutbr.cz
-- Projekt:	FLP, Haskell - Rozhodovaci strom
-- Popis:	Implementace rozhodovaciho stromu

import System.Environment (getArgs)
import System.IO (readFile)
import Data.List (sort, transpose, group, intercalate, minimumBy)

-- Read command line arguments and perform actions accordingly
main :: IO ()
main = do
    args <- getArgs
    case args of
        ["-1", input1, input2] -> do
            contents <- readFile input1
            let treeLines = lines contents
            
            let tree = createTree (removeIndent treeLines) (-1)            

            contents <- readFile input2
            let dataLines = lines contents

            let x = unlines $ map (\k->findClass tree k) ((listOfStringToDouble (map commaToSpace dataLines)))
            putStrLn (init x)
            
        ["-2", input1] -> do
            contents <- readFile input1
            let x = lines contents
            let y = map commaToSpace x
            let z = makeTriples $ transpose $ map words y
            let tree = createCARTTree z
            print tree            
                      
        _ -> putStrLn "Usage: ./flp-fun -1 <treeFile> <inputFile> or ./flp-fun -2 <inputFile>"
    

-- CREATE TREE

-- Define the Tree data type
data Tree = Empty | Leaf String | Node Int Double Tree Tree deriving(Eq)

-- Show instance for Tree data type
instance Show Tree where
  show tree = intercalate "\n" (showTreeIndented tree 0)
    where
      showTreeIndented :: Tree -> Int -> [String]
      showTreeIndented Empty _ = []
      showTreeIndented (Leaf value) level = [replicate (level * 2) ' ' ++ "Leaf: " ++ value]
      showTreeIndented (Node index threshold left right) level =
        let nodeStr = replicate (level * 2) ' ' ++ "Node: " ++ show index ++ ", " ++ show threshold
            leftStr = showTreeIndented left (level + 1)
            rightStr = showTreeIndented right (level + 1)
        in [nodeStr] ++ leftStr ++ rightStr

-- Check if a line represents a Leaf node
isLeaf :: String -> Bool
isLeaf line = "Leaf:" `elem` words line

-- Check if a line represents a Node
isNode :: String -> Bool
isNode line = "Node:" `elem` words line


-- Get the indentation level of a line
getIndentValue :: String -> Int
getIndentValue line
    | (length (words line)) < 3 = error $ "Invalid leaf indent"
    | otherwise = (read $ (last $ words line)::Int)

-- Remove indentation from lines
removeIndent :: [String] -> [String]
removeIndent [] = []
removeIndent (line:lines) = ((drop indentSize line) ++ " " ++ (show $ indentSize)) : removeIndent lines
    where indentSize = removeSpace line

-- Remove leading spaces from a line
removeSpace :: String -> Int
removeSpace [] = 0
removeSpace (character:line)
    | character /= ' ' = 0
    | character == ' ' = 1 + removeSpace line

-- Create a tree from a list of strings representing nodes
createTree :: [String] -> Int -> Tree
createTree [] _ = Empty
createTree (first:rest) parentIndent
    | parentIndent == lineIndent = Empty
    | isNode element = Node (read (init (words first !! 1))::Int) (read (words first !! 2)::Double) subTree1 subTree2
    | isLeaf element = Leaf ((words first) !! 1)
    | otherwise = error $ "First element is neither Leaf or Node"
        where
            element = head $ words first
            lineIndent = (read $ (last $ words first)::Int)
            subTree1 = (createTree rest lineIndent)
            subTree2 = (createTree (drop (findSubTree (drop 1 rest) lineIndent) rest) lineIndent)            
            index = findSubTree rest            

-- Find the indentation level of the subtree
findSubTree :: [String] -> Int -> Int
findSubTree [] _ = 0
findSubTree (first:rest) parentIndent
    | getIndentValue first == (parentIndent + 2) = 1
    | otherwise = 1 + (findSubTree rest parentIndent)

-- PROCESS INPUT

-- Replace commas with spaces in a string
commaToSpace :: String -> String
commaToSpace [] = []
commaToSpace (x:xs)
    | x == ',' = ' ': commaToSpace xs    
    | otherwise = x : commaToSpace xs

-- Find the class for a given input in the tree
findClass :: Tree -> [Double] -> String
findClass (Leaf str) _ = str
findClass _ [] = ""
findClass Empty _ = ""
findClass (Node index threshold subTree1 subTree2) xs
    |  (xs!!index) > threshold = findClass subTree2 xs
    |  (xs!!index) <= threshold = findClass subTree1 xs

-- Convert a list of strings to a list of lists of doubles
listOfStringToDouble :: [String] -> [[Double]]
listOfStringToDouble = map (map (read :: String -> Double) . words)


-- CART ALGORITHM

-- Calculate split points for values
calculateSplits :: [Double] -> [Double]
calculateSplits vals = [(x1+x2)/2 | (x1, x2) <- zip vals (tail vals)]

-- Create pairs from a list of lists
makePairs :: [[a]] -> [[(a, a)]]
makePairs lists = map (\xs -> zip xs lastList) (init lists)
  where
    lastList = last lists
    
-- Create triples from a list of lists of strings
makeTriples :: [[String]] -> [[(Double, String, Int)]]
makeTriples lists = map addIndex pairs
  where
    pairs = makePairs lists
    addIndex xs = zipWith (\(x, y) i -> (read x, y, i)) xs [0..]

-- Maximum value of Double
maxDoubleValue :: Double
maxDoubleValue = 1.7e308

-- Get the first element of a triple
getFst :: (x, y, z) -> x
getFst (x, _, _) = x

-- Get the second element of a triple
getSnd :: (x, y, z) -> y
getSnd (_, y, _) = y

-- Get the third element of a triple
getThrd :: (x, y, z) -> z
getThrd (_, _, z) = z

-- Filter triples by their third element
filterByID :: [(Double, String, Int)] -> [Int] -> [(Double, String, Int)]
filterByID tripleList intList = filter (\(_, _, x) -> x `elem` intList) tripleList

-- Get the name from a triple
getName :: (Double, String, Int) -> String
getName (_, y, _) = y

-- Convert a string to a double
stringToDouble :: String -> Double
stringToDouble str = read str

-- Count occurrences of elements in a list
countOccurrences :: Ord a => [a] -> [Int]
countOccurrences = map length . group . sort

-- Calculate probabilities from counts
probabilities :: [Int] -> [Double]
probabilities values = map (\x -> fromIntegral x / totalSum) values
  where totalSum = fromIntegral (sum values)

-- Calculate the Gini impurity for a set of values
gini :: [Double] -> Double -> [String] -> ([String],[String]) -> ([String],[String])
gini [] _ _ (left,right) = (left,right)
gini (x:xs) threshold (name:className) (left,right)
    | x > threshold = gini xs threshold className (left,right++[name])
    | otherwise = gini xs threshold className (left++[name],right)

-- Gini impurity for two children
gini2 :: [Double] -> Double -> [Int] -> ([Int],[Int]) -> ([Int],[Int])
gini2 [] _ _ (left, right) = (left, right)
gini2 (x:xs) threshold (i:ids) (left, right)
    | x <= threshold = gini2 xs threshold ids (i:left, right)
    | otherwise = gini2 xs threshold ids (left, i:right)


-- Extract the values from triples
extractValues :: [(Double, String, Int)] -> [Double]
extractValues pairs = map getFst pairs

-- Extract the names from triples
extractNames :: [(Double, String, Int)] -> [String]
extractNames pairs = map getSnd pairs

-- Extract the IDs from triples
extractIDs :: [(Double, String, Int)] -> [Int]
extractIDs pairs = map getThrd pairs

-- Create a decision using CART algorithm from a list of input data
createCARTTree :: [[(Double, String, Int)]] -> Tree
createCARTTree [] = Empty
createCARTTree xs
    | classCount == 1 = (Leaf (names!!0))
    | leftChildNodeCount == 1 && rightChildNodeCount == 1 = Node thresholdIndex bestThreshold (Leaf leftLeafName) (Leaf rightLeafName)
    | leftChildNodeCount == 1 && rightChildNodeCount == 0 = Node thresholdIndex bestThreshold (Leaf leftLeafName) Empty
    | leftChildNodeCount == 0 && rightChildNodeCount == 1 = Node thresholdIndex bestThreshold Empty (Leaf rightLeafName)
    | leftChildNodeCount == 0 = Node thresholdIndex bestThreshold Empty (createCARTTree xsRight)
    | rightChildNodeCount == 0 = Node thresholdIndex bestThreshold (createCARTTree xsLeft) Empty
    | rightChildNodeCount == 1 = Node thresholdIndex bestThreshold (createCARTTree xsLeft) (Leaf rightLeafName)
    | leftChildNodeCount == 1 = Node thresholdIndex bestThreshold (Leaf leftLeafName) (createCARTTree xsRight)
    | otherwise = Node thresholdIndex bestThreshold (createCARTTree xsLeft) (createCARTTree xsRight)
    where
        tripples = xs
        allValues = map extractValues tripples
        names = extractNames (tripples!!0)
        ids = extractIDs (tripples!!0)
        classCount = length $ countOccurrences $ names
        allSplits = map calculateSplits (map sort allValues)        
        allThresholds = map (\k->findBestThreshold k 0.0 maxDoubleValue names) (zip allSplits allValues)
        (bestThreshold, thresholdIndex) = minIndex allThresholds

        values = (allValues!!thresholdIndex)
        children = gini2 values bestThreshold ids ([],[])
        leftChild = sort $ fst children
        rightChild = sort $ snd children
        rightTreeElements = filterByID (xs!!thresholdIndex) rightChild
        leftTreeElements = filterByID (xs!!thresholdIndex) leftChild
        leftLeafName = getName (leftTreeElements!!0)
        rightLeafName = getName (rightTreeElements!!0)
        leftChildNodeCount = length $ countOccurrences $ extractNames leftTreeElements
        rightChildNodeCount = length $ countOccurrences $ extractNames rightTreeElements
        xsRight = map (\k-> filterByID k rightChild) xs
        xsLeft = map (\k-> filterByID k leftChild) xs

-- Find the index of an element in a list
findIndex :: Double -> [Double] -> Int -> Int
findIndex _ [] _ = 0
findIndex elem (x:xs) counter
    | elem == x = counter
    | otherwise = findIndex elem xs (counter+1)

-- Find the index of the minimum value in a list of pairs
minIndex :: [(Double, Double)] -> (Double, Int)
minIndex xs = let (_, minIndex) = minimumBy (\(a, _) (b, _) -> compare a b) (zip (map snd xs) [0..])
                      in (fst (xs !! minIndex), minIndex)    

-- Find the best threshold for splitting
findBestThreshold :: ([Double],[Double])->Double->Double->[String]->(Double,Double)
findBestThreshold ([],_) threshold giniTotal _ = (threshold,giniTotal)
findBestThreshold ((x:xs),values) threshold giniTotal parentList
    | total < giniTotal = findBestThreshold (xs,values) x total parentList
    | otherwise = findBestThreshold (xs,values) threshold giniTotal parentList
    where
        children = gini values x parentList ([],[])

        giniChild1 = countOccurrences $ fst children 
        prob_giniChild1 = probabilities giniChild1 
        k = (sum $ (map (\k->k*(1-k)) prob_giniChild1))

        giniChild2 = countOccurrences $ snd children
        prob_giniChild2 = probabilities giniChild2
        t =  (sum $ (map (\k->k*(1-k)) prob_giniChild2))
        
        parentSum = length parentList
        multiplier_Child1 = (fromIntegral $ length $ fst children )/(fromIntegral $ parentSum)
        multiplier_Child2 = (fromIntegral $ length $ snd children )/(fromIntegral $ parentSum)
        total = (multiplier_Child1*k)+(multiplier_Child2*t)        

